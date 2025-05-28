from aiogram.types import BotCommand

async def set_bot_commands(bot):
    commands= [
        BotCommand(command="start", description="Start the bot."),
        BotCommand(command="scan_file", description="Upload a file to scan it for viruses, malware, and threats."),
        BotCommand(command="scan_url", description="Submit a URL to check for phishing, malware, or suspicious content.")
    ]

    await bot.set_my_commands(commands)