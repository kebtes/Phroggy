from pathlib import Path
import asyncio
import aiohttp

import pendulum

from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.states import ScanFileStates
from services.check_file import check_file
from core.handlers.commands import router
from services.check_file import ACCEPTED_FILE_TYPES

from services.check_file import scanner

current_prompts = []

FILE_SIZE_LIMIT = 20 * 10**6

async def analyze_report(report: dict, file_name: str):
    """
    Parses and evaluates the scan report.
    Returns:
        - formatted HTML report string
        - whether file is flagged as malicious/suspicious (bool)
    """

    THRESHOLD = 0.5
    CATEGORIES = ['malicious', 'suspicious']

    REPORT_TEMPLATE = (
        "<b>{file_name}</b>\n\n"

        "<b>Scan Status:</b> {status}\n"
        "<b>Date Scanned:</b> {scan_date}\n\n"

        "🔑 <u><b>Hash</b></u>\n"
        "<b>MD5 Hash: </b> <code>{md5}</code>\n"
        "<b>SHA-256 Hash: </b> <code>{sha256}</code>\n"
        "<b>SHA-1 Hash: </b> <code>{sha1}</code>\n\n"

        "<b>🔍 Detection Summary <u>(Summary Across Various Antiviruses):</u></b>\n"
        "- Malicious: {malicious}\n"
        "- Suspicious: {suspicious}\n"
        "- Harmless: {harmless}\n"
        "- Undetected: {undetected}\n"
        "- Timeout: {timeout}\n\n"

        '<a href="https://www.virustotal.com/gui/file/{sha256}/detection">🦠 View Full Report</a>'
    )
    
    try:
        attributes = report["data"]["attributes"]
        results = attributes["stats"]
        details = attributes["results"]
        file_info = report["meta"]["file_info"]

        report_data = {
            "status"        : attributes.get("status", "Unknown").capitalize(),
            "scan_date"     : pendulum.now("UTC").format("YYYY-MM-DD HH:mm:ss"),
            "sha256"        : file_info.get("sha256", "N/A"),
            "sha1"          : file_info.get("sha1", "N/A"),
            "md5"           : file_info.get("md5", "N/A"),
            "file_name"     : file_name,
            "malicious"     : results.get("malicious", 0),
            "suspicious"    : results.get("suspicious", 0),
            "harmless"      : results.get("harmless", 0),
            "undetected"    : results.get("undetected", 0),
            "timeout"       : results.get("timeout", 0),
        }

        total_engines = len(details)
        flagged_engines = sum(1 for result in details.values()
                              if result.get("category") in CATEGORIES)

        report_str = REPORT_TEMPLATE.format(**report_data)

        is_flagged = (flagged_engines / total_engines) > THRESHOLD if total_engines > 0 else False
        return report_str, is_flagged

    except KeyError as e:
        print(f"[Error] Missing key in report: {e}")
        print("Full report:", report)
        raise

@router.message(Command("scan_file"))
async def ask_for_file(message: types.Message, state: FSMContext):
    await message.answer("Please go ahead and send the file you’d like me to scan.")
    await state.set_state(ScanFileStates.waiting_for_file)

@router.message(ScanFileStates.waiting_for_file, F.document)
async def handle_file(message: types.Message, state: FSMContext):
    document = message.document
    
    # check file size before moving forward
    if document.file_size > FILE_SIZE_LIMIT:
        await message.reply("The file exceeds the Telegram bot upload limit.\nPlease send a file smaller than <b>20 MB.</b>")
    
    else:
        file = await message.bot.get_file(document.file_id)
        
        ROOT_DIR = Path(__file__).resolve().parent.parent.parent
        TEMP_DIR = ROOT_DIR / "temp"
        TEMP_DIR.mkdir(exist_ok=True)

        relative_file_path = Path("temp") / file.file_path
        absolute_file_path = ROOT_DIR / relative_file_path

        try:
            absolute_file_path.parent.mkdir(parents=True, exist_ok=True)

            await message.bot.download_file(file.file_path, destination=absolute_file_path)

            file_recieved_msg = await message.answer("File recieved. Scanning...")

            response = await scanner(absolute_file_path)
            # response = await check_file(absolute_file_path)

            if "error" in response:
                error = response["error"]
                if error == "ERROR_FILE_TYPE_NOT_SUPPORTED":
                    file_type = response["file_type"]
                    response_msg = (
                        f"Sorry, we don't support <b>{file_type}</b> file types at the moment.\n\n"
                        "<u><b>Accepted file types include</b></u>\n"
                        "<code>"
                        f"{', '.join(ACCEPTED_FILE_TYPES)}"
                        "</code>\n\n"
                        "Please upload a <b>supported</b> file format."
                    )
                    await message.reply(response_msg)
                
                elif error == "ERROR_PASSWORD_PROTECTED":
                    response_msg = (
                        "This file appears to be <b>password-protected</b> and cannot be processed automatically. "
                        "Please provide an unprotected version of the file."
                    )

                    await message.reply(response_msg)

                elif error == "ERROR_FAILED_TO_RESPOND_ON_TIME":
                    response_msg = (
                        "Looks like the servers are a bit busy right now. Try again in a moment!"
                    )

                    await message.reply(response_msg)
                    
            else:
                report, _ = await analyze_report(response, file_name=document.file_name)
                await message.reply(report)
            
            await message.bot.delete_message(chat_id = message.chat.id, message_id=file_recieved_msg.message_id)

        except asyncio.TimeoutError:
            print("Time out while downloading file")

        except aiohttp.ClientError:
            print("Connection problem")

        except Exception as e:
            print(f"Unknown Error: {e}")

        absolute_file_path.unlink(missing_ok=True)
    
    await state.clear()

@router.message(ScanFileStates.waiting_for_file)
async def file_not_sent(message: types.Message):
    current_prompts.append(await message.answer("Please send a valid file."))
