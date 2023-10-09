from os import environ

BOT_TOKEN = environ['BOT_TOKEN']

# For local development:
# DATABASE_ENGINE = environ['DATABASE_ENGINE']
# DATABASE_NAME = environ['DATABASE_NAME']
# DATABASE_USER = environ['DATABASE_USER']
# DATABASE_PASSWORD = environ['DATABASE_PASSWORD']
# DATABASE_HOST = environ['DATABASE_HOST']
# DATABASE_PORT = environ['DATABASE_PORT']

# Or just use DATABASE_URL from Heroku:
DATABASE_URL = environ['DATABASE_URL']

WEBAPP_URL = environ['WEBAPP_URL']

PROVIDER_TOKEN = environ['PROVIDER_TOKEN']

DJANGO_SECRET_KEY = environ['DJANGO_SECRET_KEY']

# For server-side webhook:
# WEBHOOK_SECRET = environ['WEBHOOK_SECRET']
#
# BASE_WEBHOOK_URL = environ['BASE_WEBHOOK_URL']
