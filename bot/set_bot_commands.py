from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats, BotCommandScopeAllGroupChats

async def set_bot_commands(bot):
    main_commands= [
        BotCommand(command="start", description="Start the bot."),
        BotCommand(command="scan_file", description="Upload a file to scan it for malware and threats."),
        BotCommand(command="scan_url", description="Submit a URL to check for phishing or malware."),
        BotCommand(command="link_group", description="Add the bot to a group chat."),
        BotCommand(command="my_groups", description="Remove the bot from a group chat."),
        BotCommand(command="help", description="List all commands and how to use them.")
    ]

    await bot.set_my_commands(
        main_commands,
        scope=BotCommandScopeAllPrivateChats()
        )
    
    group_commands = [
        BotCommand(command="add_moderator", description="Give a user permission to use admin bot commands."),
        BotCommand(command="auto_delete", description="Turn on automatic deletion of flagged messages."),
        BotCommand(command="blacklist_keyword", description="Block certain keywords in messages."),
        BotCommand(command="blaclist", description="Block a user from sending links or files."),
        BotCommand(command="hisotry", description="Show a log of flagged messages from the past week."),
        BotCommand(command="notify_admins", description="Notify admins when a message is flagged."),
        BotCommand(command="notify_users", description="Notify all users when a message is flagged."),
        BotCommand(command="pause_scan", description="Temporarily stop scanning."),
        BotCommand(command="sensitivity", description="Change how strict the scan is."),
        # BotCommand(command="set_scan_interval", description="Change how often scans happen."),
        BotCommand(command="skip", description="Ignore specific URLs or file types during scans."),
        BotCommand(command="whitelist", description="Allow a specific user's messages to bypass scanning."),
        BotCommand(command="id", description="Used to ID the group with the bot.")
    ]

    await bot.set_my_commands(
        group_commands,
        scope=BotCommandScopeAllGroupChats()
    )