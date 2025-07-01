# This file serves as the HTTP entrypoint for the bot's webhook.
# It exposes an aiohttp web application instance that handles incoming
# Telegram webhook requests.

from bot.main import create_app

app = create_app()
