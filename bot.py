import asyncio
import datetime
import logging
import os
import ssl
from urllib.parse import quote
from typing import Union, Tuple

import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

from webapp.mysecrets import BOT_TOKEN, WEBAPP_URL, WEBHOOK_SECRET, BASE_WEBHOOK_URL  # Importing mysecrets (BOT_TOKEN and WEBAPP_URL)

from aiohttp import web

from aiogram import Router
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

# Webserver settings
WEB_SERVER_HOST = "0.0.0.0"
WEB_SERVER_PORT = int(os.getenv('PORT', 8443))

# Path to webhook route, on which Telegram will send requests
WEBHOOK_PATH = "/webhook"


# Configure logging for the application
logging.basicConfig(level=logging.INFO)

# Initialize the bot and dispatcher
bot = Bot(token=BOT_TOKEN)  # Create a bot instance using the provided BOT_TOKEN
dp = Dispatcher()

router = Router()


async def on_startup(bot: Bot) -> None:
    # In case when you have a self-signed SSL certificate, you need to send the certificate
    # itself to Telegram servers for validation purposes
    # (see https://core.telegram.org/bots/self-signed)
    # But if you have a valid SSL certificate, you SHOULD NOT send it to Telegram servers.
    await bot.set_webhook(
        f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}",
        # certificate=FSInputFile(WEBHOOK_SSL_CERT),
        secret_token=WEBHOOK_SECRET,
    )


# Define an asynchronous function to process incoming events
async def process_event(event: Union[types.Message, types.CallbackQuery], with_user_id: bool = False) -> Union[
    types.Message, Tuple[types.Message, int]]:
    """
    Process incoming events (messages or callback queries).

    Args:
        event (Union[types.Message, types.CallbackQuery]): The incoming event to be processed.
        with_user_id (bool, optional): Whether to include the user ID in the result. Default is False.

    Returns:
        Union[types.Message, Tuple[types.Message, int]]: Processed message or message with user ID if 'with_user_id' is True.
    """
    # Check the type of event (message or callback query) and extract the message
    if type(event) is types.Message:
        message = event
    else:
        await bot.answer_callback_query(event.id)
        message = event.message

    # Return the message with or without the user ID based on the 'with_user_id' parameter
    if not with_user_id:
        return message
    else:
        return message, event.from_user.id


# Define an asynchronous function to deliver a message to the chat
async def deliver_message(event: Union[types.Message, types.CallbackQuery], init_message_editable: bool, **kwargs):
    """
    Deliver a message to the chat.

    Args:
        event (Union[types.Message, types.CallbackQuery]): The incoming event that triggered this message.
        init_message_editable (bool): Whether the initial message is editable (for callback queries).
        **kwargs: Additional keyword arguments, including 'text' and 'reply_markup'.
    """
    # Process the incoming event to get the message
    message = await process_event(event)

    # Check if the event is a callback query and if the initial message is editable
    if type(event) is types.CallbackQuery and init_message_editable:
        # Edit the message text and reply markup
        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text=kwargs['text'],
            reply_markup=kwargs['reply_markup']
        )
    else:
        # Send a new message with Markdown parsing and reply markup
        await bot.send_message(
            chat_id=message.chat.id,
            text=kwargs['text'],
            parse_mode='Markdown',
            reply_markup=kwargs['reply_markup']
        )


# Define a handler for the '/start' or 'main' command and display a menu
@dp.message(Command("start", "main"))
@dp.callback_query(lambda callback_query: callback_query.data == 'menu')
async def menu(event: Union[types.Message, types.CallbackQuery], init_message_editable: bool = True):
    """
    Handle the '/start' or 'main' command and display a menu.

    Args:
        event (Union[types.Message, types.CallbackQuery]): The incoming event that triggered this menu.
        init_message_editable (bool, optional): Whether the initial message is editable (for callback queries). Default is True.
    """
    if type(event) is types.Message:
        msg_id = event.message_id
    else:
        msg_id = event.message.message_id
    # Define inline keyboard markup for the menu
    inline_keyboard_markup = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Services", web_app=types.WebAppInfo(
            url=f'{WEBAPP_URL}/make_order?init_message_id={msg_id}'))],
        [types.InlineKeyboardButton(text="Information", callback_data='info')],
        [types.InlineKeyboardButton(text="Active Appointments", callback_data='active')]
    ])

    # Deliver the menu message
    await deliver_message(event, init_message_editable, text="Menu", reply_markup=inline_keyboard_markup)


# Define a handler for pre-checkout queries during payment processing
@dp.pre_checkout_query(lambda pre_checkout_query: True)
async def pre_checkout(pre_checkout_query: types.PreCheckoutQuery):
    """
    Handle pre-checkout queries during payment processing.

    Args:
        pre_checkout_query (types.PreCheckoutQuery): The pre-checkout query to be handled.
    """
    # Answer the pre-checkout query with 'ok'
    await bot.answer_pre_checkout_query(
        pre_checkout_query_id=pre_checkout_query.id,
        ok=True
    )


# Define a handler for successful payment confirmation and create an appointment
@dp.message(F.content_type == types.ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    """
    Handle successful payment confirmation and create an appointment.

    Args:
        message (types.Message): The message containing successful payment information.
    """
    # Extract payment-related data from the message
    invoice_payload = message.successful_payment.invoice_payload
    user_id, init_message_id, services_ids, date_iso, time_iso = invoice_payload.split()
    user_id, init_message_id = int(user_id), int(init_message_id)

    # Make a request to create an appointment using the provided data
    requests.get(f'{WEBAPP_URL}/make_appointment', {
        'bot_token': BOT_TOKEN,
        'user_id': user_id,
        'services_ids': services_ids,
        'date_iso': date_iso,
        'time_iso': time_iso,
    }, verify=False)

    # Delete the initial message related to the payment
    await bot.delete_message(
        chat_id=message.chat.id,
        message_id=init_message_id
    )

    # Send a sticker and a thank you message
    await bot.send_sticker(
        chat_id=message.chat.id,
        sticker="CAACAgIAAxkBAAEKe9ZlIw3TExDaMwa64M6RmQvmtfdTowACkygAAoKzqEnhVTaaypbA5DAE"
    )

    await bot.send_message(
        chat_id=message.chat.id,
        text="Thank you for your appointment! Your appointment has been successfully created. We look forward to seeing you at the salon!"
    )

    # Return to the main menu
    await menu(message, init_message_editable=False)


# Define a handler to display information about the salon
@dp.message(Command('info'))
@dp.callback_query(lambda callback_query: callback_query.data == 'info')
async def info(event: Union[types.Message, types.CallbackQuery], init_message_editable: bool = True):
    """
    Display information about the salon.

    Args:
        event (Union[types.Message, types.CallbackQuery]): The incoming event that triggered this information display.
        init_message_editable (bool, optional): Whether the initial message is editable (for callback queries). Default is True.
    """
    # Define inline keyboard markup for salon information
    inline_keyboard_markup = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Address", callback_data='address')],
        [types.InlineKeyboardButton(text="Contacts", callback_data='contacts')],
        [types.InlineKeyboardButton(text="< Menu", callback_data='menu')]
    ])

    text = "🕓 We are open every day from 9:00 AM to 8:00 PM"

    # Deliver the salon information message
    await deliver_message(event, init_message_editable, text=text, reply_markup=inline_keyboard_markup)


# Define a handler to display the salon's address
@dp.callback_query(lambda callback_query: callback_query.data == 'address')
async def address(event: Union[types.Message, types.CallbackQuery]):
    """
    Handle the 'address' callback query and display the salon's address.

    Args:
        event (Union[types.Message, types.CallbackQuery]): The incoming event that triggered this address display.
    """
    # Process the incoming event to get the message
    message = await process_event(event)

    text = "Narrows Rd S, Staten Island, NY, US"

    # Edit the message to display the salon's address and send the location
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=text
    )

    await bot.send_location(
        chat_id=message.chat.id,
        latitude=40.607083,
        longitude=-74.087041
    )

    await info(message, init_message_editable=False)


# Define a handler to display salon contact information
@dp.callback_query(lambda callback_query: callback_query.data == 'contacts')
async def contacts(event: Union[types.Message, types.CallbackQuery]):
    """
    Handle the 'contacts' callback query and display salon contact information.

    Args:
        event (Union[types.Message, types.CallbackQuery]): The incoming event that triggered this contact information display.
    """
    # Process the incoming event to get the message
    message = await process_event(event)

    # Delete the initial message related to the contact information
    await bot.delete_message(
        chat_id=message.chat.id,
        message_id=message.message_id
    )

    # Send salon contact information as a contact card
    await bot.send_contact(
        chat_id=message.chat.id,
        phone_number="+11111111111",
        first_name="BeautyBloomSalonBot"
    )

    await info(message, init_message_editable=False)


# Define a handler for the '/active' command or 'active' callback query to display active appointments for the user
@dp.message(Command('active'))
@dp.callback_query(lambda callback_query: callback_query.data == 'active')
async def active(event: Union[types.Message, types.CallbackQuery]):
    """
    Handle the '/active' command or 'active' callback query to display active appointments for the user.

    Args:
        event (Union[types.Message, types.CallbackQuery]): The incoming event that triggered the display of active appointments.
    """
    # Process the incoming event to get the message and user ID
    message, user_id = await process_event(event, with_user_id=True)

    # Make a request to get the user's active appointments
    response = requests.get(f'{WEBAPP_URL}/get_active_appointments', {
        'bot_token': BOT_TOKEN,
        'user_id': user_id
    }, verify=False)

    active_appointments = response.json()['active_appointments']

    if len(active_appointments) == 0:
        # If there are no active appointments, display a message with a back to menu button
        inline_keyboard_markup = types.InlineKeyboardMarkup(
            inline_keyboard=[[types.InlineKeyboardButton(text="< Menu", callback_data='menu')]])
        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text="You don't have any active appointments yet",
            reply_markup=inline_keyboard_markup
        )
        return None

    inline_keyboard_markup = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text="< Menu", callback_data="menu")]]
    )

    text = ""
    # Add text about all active appointments
    for i in range(len(active_appointments)):
        date_formatted = datetime.date.fromisoformat(active_appointments[i]["date"]).strftime("%B, %d")
        time_formatted = datetime.time.fromisoformat(active_appointments[i]["time"]).strftime("%H:%M")
        text += f"Date: *{date_formatted}*\nTime: *{time_formatted}*\nServices:\n"
        for service_title in active_appointments[i]['services_titles']:
            text += f"\n— *{service_title}*"

        text += "\n\n"

    # Edit the message to display the active appointments with Markdown parsing
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=text,
        parse_mode='Markdown',
        reply_markup=inline_keyboard_markup
    )


# Define a handler to handle pagination for active appointments
@dp.callback_query(lambda callback_query: callback_query.data.startswith('active_nav'))
async def active_nav(callback_query: types.CallbackQuery):
    """
    Handle pagination for active appointments.

    Args:
        callback_query (types.CallbackQuery): The callback query containing pagination information.
    """
    callback_query_data_split = callback_query.data.split()
    active_appointment_idx = int(callback_query_data_split[-1])

    if callback_query_data_split[1] == 'prev':
        await active(callback_query, active_appointment_idx - 1)
    else:
        await active(callback_query, active_appointment_idx + 1)


# Define the main asynchronous function to start polling the bot for incoming events
async def main():
    """
    Main function to start polling the bot for incoming events.
    """
    await dp.start_polling(bot)


# Check if the script is being run directly
if __name__ == '__main__':
    # Local run and develop
    asyncio.run(main())  # Run the main function to start polling the bot

    # # Server setup
    # dp.include_router(router)
    #
    # # Register startup hook to initialize webhook
    # dp.startup.register(on_startup)
    #
    # # Create aiohttp.web.Application instance
    # app = web.Application()
    #
    # # Create an instance of request handler,
    # # aiogram has few implementations for different cases of usage
    # # In this example we use SimpleRequestHandler which is designed to handle simple cases
    # webhook_requests_handler = SimpleRequestHandler(
    #     dispatcher=dp,
    #     bot=bot,
    #     secret_token=WEBHOOK_SECRET,
    # )
    # # Register webhook handler on application
    # webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    #
    # # Mount dispatcher startup and shutdown hooks to aiohttp application
    # setup_application(app, dp, bot=bot)
    #
    # # And finally start webserver
    # web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)
