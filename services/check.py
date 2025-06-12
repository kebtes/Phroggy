from aiogram.types import Document, Message
from services import check_file, check_spam, check_url
from db import groups
from pathlib import Path

sensitivity_thresholds = {
    "low": 0.5,
    "moderate": 0.8,
    "high": 0.7
}

async def check(text: str, document: Document, group_id: int, message: Message):
    """
    output should be in the form of

    {
        url: [Bool, flagged urls],
        file: Bool,
        spam: Bool
    }
    """
    output = {}

    # fetch group settings
    group_info = await groups.group_info(group_id)
    
    # * LINKS
    try:
        skip = set(group_info.get("skip_links", [])) 
        resp = await check_url.check_url(text, skip)
        if resp:
            threat_found = resp[0]
            if threat_found:
                output["link"] = resp[1]
            else:
                output["link"] = False
    
    except Exception:
        # TOOD add a logger here
        pass

    # * FILES
    try:
        skip_files = set(group_info.get("skip_urls", []))
        
        # check if its skippable
        mime_type = document.mime_type
        _, ext = mime_type.split("/")
        if ext not in skip_files:
            file = await message.bot.get_file(document.file_id)

            ROOT_DIR = Path(__file__).resolve().parent.parent.parent
            TEMP_DIR = ROOT_DIR / "temp"
            TEMP_DIR.mkdir(exist_ok=True)

            relative_file_path = Path("temp") / file.file_path
            absolute_file_path = ROOT_DIR / relative_file_path
            absolute_file_path.parent.mkdir(parents=True, exist_ok=True)

            await message.bot.download_file(file.file_path, destination=absolute_file_path)
            response = await check_file.scanner(absolute_file_path)

            if "error" in response:
                error = response["error"]
                if error == "ERROR_FILE_TYPE_NOT_SUPPORTED":
                    pass

                elif error == "ERROR_PASSWORD_PROTECTED":
                    pass

                elif error == "ERROR_FAILED_TO_RESPOND_ON_TIME":
                    pass

            else:
                attributes = response["data"]["attributes"]
                results = attributes["stats"]
                malicious = results.get("malicious", 0)
                suspicous = results.get("suspicious", 0)

                output["file"] = True if malicious > 0 or suspicous > 0 else False
    
    except Exception:
        # logg this shit
        pass

    # SPAM
    try:
        spam_sensitivity = group_info.get("spam_sensitivity", "moderate")
        sensitivity = sensitivity_thresholds[spam_sensitivity]
        
        is_spam = await check_spam.spam(text, sensitivity)
        output["spam"] = is_spam

    except Exception:
        # add a fckn logger here
        pass
    
    return output