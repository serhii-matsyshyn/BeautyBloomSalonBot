# BeautyBloomSalonBot - Telegram Bot for Beauty Salon

@BeautyBloomSalonBot is a demo Telegram bot based on Mini App that allows users to choose services and make appointments at the beauty salon, and pay for services using the built-in Telegram payment provider.  
**It is based on Mini App!**  
The web app for handling appointments is powered by Django, aiogram, and PostgreSQL. It is hosted at Heroku. This README provides detailed instructions on how to set up and use the bot.  
**Try this bot in action: [@BeautyBloomSalonBot](https://t.me/BeautyBloomSalonBot)**

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Certificate Setup](#certificate-setup)
- [Local Development](#local-development)
- [Deployment](#deployment)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
- [Test it now!](#test-it-now)
- [Contributing](#contributing)
- [License](#license)

## Prerequisites

Before you begin, ensure you have the following prerequisites:
- Python 3.x
- PostgreSQL
- Telegram Bot Token (BOT_TOKEN)
- Django Secret Key (DJANGO_SECRET_KEY)
- Telegram Payment Provider Token (PROVIDER_TOKEN)

## Installation

To install and set up BeautyBloomSalonBot, follow these steps:

1. Clone the repository:

   ```shell
   git clone https://github.com/your-repo/BeautyBloomSalonBot.git
   cd BeautyBloomSalonBot
2. Create a virtual environment (optional but recommended):

    ```shell
    python -m venv venv
    source venv/bin/activate
    ```

3. Install the required dependencies:
    ```shell
    pip install -r requirements.txt
    ```

## Configuration
Configure the bot and database settings by setting the following environment variables:

```shell
BOT_TOKEN = <Your Telegram Bot Token>
DATABASE_ENGINE = <Database Engine (e.g., postgresql)>
DATABASE_NAME = <Database Name>
DATABASE_USER = <Database User>
DATABASE_PASSWORD = <Database Password>
DATABASE_HOST = <Database Host>
DATABASE_PORT = <Database Port>

# Or just use DATABASE_URL from Heroku:
DATABASE_URL = <Database URL>

PROVIDER_TOKEN = <Telegram Payment Provider Token>
DJANGO_SECRET_KEY = <Django Secret Key>

WEBAPP_URL = <Web App URL>

# For server-side webhook:
# WEBHOOK_SECRET = <Webhook Secret>
#
# BASE_WEBHOOK_URL = <Base Webhook URL>
```

Run Django migrations:

```shell
python webapp/manage.py makemigrations
python webapp/manage.py migrate
```

## Certificate Setup
To enable secure connections for your local development environment, follow these steps:

Generate a self-signed certificate:

```shell
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/CN=localhost/C=US/ST=/L=/O=/OU=/emailAddress="
ATTENTION: Never use this certificate in a production environment.
```
If you encounter any certificate-related issues (e.g., "Your connection is not private"), refer to the [certificate setup instructions](https://core.telegram.org/bots/self-signed) and [hints](https://docs.ton.org/develop/dapps/telegram-apps/app-examples#hints).

## Local Development
To run BeautyBloomSalonBot locally with secure connections, use the following commands:

```shell
python webapp/manage.py runserver_plus --cert-file cert.pem --key-file key.pem
python bot.py
```

To add a new user to th django admin panel, use the following command:

```shell
python webapp/manage.py createsuperuser
```

Then in your browser, navigate to https://localhost:8000/admin and log in with the credentials you created.  
You will be able to add or edit Services, and set price for each service.

For default, the appointment time is set to 1 hour. It can be easily customized if you want to add some new functionality (for instance, set specific time it takes for some service etc).  
By default, the appointments are created only after the payment is successful. If you need to store appointments even if the payment is not successful (or save payment time etc), you can easily customize it in the code.

## Usage:
To use BeautyBloomSalonBot as a user, follow these steps:
- Start the bot by sending the /start command.
- Open the web app by clicking the link in the bot's welcome message.
- Choose services
- Choose date and time
- Pay for services using the built-in Telegram payment provider
- Success! You can now see your appointment in the Active Appointments section of the web app.
- You can see the address of the salon in the menu of the bot.

To use BeautyBloomSalonBot as an administrator, follow these steps:
- Open the admin panel by opening Django admin panel (https://localhost:8000/admin) and log in with the credentials you created.
- You can see all the appointments in the Appointments section.
- You can add services in the Services section.


## Deployment
To deploy BeautyBloomSalonBot to Heroku, follow the steps from the [official tutorials](https://devcenter.heroku.com/categories/python-support). It is easy, and if you follow the instructions, you will be able to deploy your bot in no time (in less then 10 minutes).  
Make sure to set the environment variables in Heroku as well, and to add the PostgreSQL add-on. Use strong passwords for your database and admin panel.
Modify the Procfile to match your project structure, and edit mysecrets.py to match your environment and bot.py (db type etc) - see comments in files.  
To deploy on heroku, use 2 dynos (1 for the bot, 1 for the web app). Edit the Procfile accordingly.  

## Troubleshooting
If you encounter any issues, please refer to the [official documentation](https://core.telegram.org/bots).  
Common issues:
- If you try to use the test bot [@BeautyBloomSalonBot](https://t.me/BeautyBloomSalonBot) and SLUG_INVALID occurs during payment, try to pay again, it is the Telegram side issue.  
- If the bot does not respond, make sure you have set the environment variables correctly and that the bot is running. Check every part of the bot (web app, bot, database) separately to see if it works.
- If you encounter any certificate-related issues (e.g., "Your connection is not private"), refer to the [certificate setup instructions](https://core.telegram.org/bots/self-signed) and [hints](https://docs.ton.org/develop/dapps/telegram-apps/app-examples#hints).
- If you encounter any issues with the payment, make sure you have set up payment provider in BotFather correctly. Also, make sure you have set up the environment variables correctly.
- If you encounter any issues with the database, use external tools to check if the database is working correctly. 
- Make sure to run Django migrations before you start the bot for the first time. Run the migrations after you add new models as well.
- Slow Response Time. If the bot responds slowly, optimize your bot's code and hosting infrastructure to reduce response times. Consider upgrading your hosting plan if necessary.
- Date and Time Format Errors. If users encounter date and time format errors, make sure you have specified your country and timezone id Django settings.py.
- If you have security concerns, implement secure authentication and authorization mechanisms to protect user data. Regularly update your bot's security practices. This bot is not intended for production use, so make sure to implement security measures if you want to use it in production.

## Test it now!
Since it is deployed on Heroku, it may take some time to start the bot after the time of inactivity.  
Try this bot in action: [@BeautyBloomSalonBot](https://t.me/BeautyBloomSalonBot)  
For payments, use test stripe card 4242424242424242, any future date, any CVC, and any other data.

## Contributing
If you'd like to contribute to BeautyBloomSalonBot, please follow our contribution guidelines.

## License
This project is licensed under the MIT License.