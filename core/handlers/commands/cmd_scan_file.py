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

current_prompts = []

FILE_SIZE_LIMIT = 20 * 10**6

REPORT_TEMPLATE = """
<b>FILE SCAN REPORT</b>

<b>File Name:</b> <i>{file_name}</i>
<b>Scan Status:</b> <i>{status}</i>
<b>Date Scanned:</b> <i>{scan_date}</i>
<b>SHA-256 Hash:</b> <i>{sha256}</i>

<b>🔍 Detection Summary:</b>
- Malicious: {malicious}
- Suspicious: {suspicious}
- Harmless: {harmless}
- Undetected: {undetected}
- Timeout: {timeout}

<a href="https://www.virustotal.com/gui/file/{sha256}/detection">🔗 View Full Report</a>
"""

async def analyze_report(report: dict, file_name: str):
    """
    Parses and evaluates the scan report.
    Returns:
        - formatted HTML report string
        - whether file is flagged as malicious/suspicious (bool)
    """

    THRESHOLD = 0.5
    CATEGORIES = ['malicious', 'suspicious']

    try:
        attributes = report["data"]["attributes"]
        results = attributes["stats"]
        details = attributes["results"]
        file_info = report["meta"]["file_info"]

        report_data = {
            "status"        : attributes.get("status", "Unknown").capitalize(),
            "scan_date"     : pendulum.now("UTC").format("YYYY-MM-DD HH:mm:ss"),
            "sha256"        : file_info.get("sha256", "N/A"),
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

            response = await check_file(absolute_file_path)
            
            if response[0].startswith("ERROR_FILE_TYPE_NOT_SUPPORTED"):
                response_msg = response = (
                    "<b>Unsupported file type.</b>\n\n"
                    "<b>Allowed file types include:</b>\n"
                    "<b>Executables & Binaries:</b> .exe, .dll, .msi, .sys, .scr, .com, .bat, ELF, Mach-O\n"
                    "<b>Documents:</b> .doc, .docx, .xls, .xlsx, .ppt, .pptx, .pdf, .rtf, .txt, .odt\n"
                    "<b>Archives:</b> .zip, .rar, .7z, .tar, .gz, .bz2\n"
                    "<b>Media:</b> .jpg, .png, .gif, .bmp, .ico, .mp3, .mp4, .avi, .mkv\n"
                    "<b>Scripts and Code:</b> .js, .vbs, .ps1, .py, .sh, .java, .class, .jar\n"
                    "<b>Other:</b> .apk, .iso, .img, .bin, .hex, .ps, .lnk\n\n"
                    "Please upload a <b>supported</b> file format."
                )

                await message.reply(response_msg)

            else:
                report, _ = await analyze_report(response, file_name = document.file_name)
                
                await message.reply(report)    
            
            await message.bot.delete_message(chat_id = message.chat.id, message_id=file_recieved_msg.message_id)

        except asyncio.TimeoutError:
            print("Time out while downloading file")

        except aiohttp.ClientError:
            print("Connection problem")

        except Exception as e:
            print(e)

        absolute_file_path.unlink(missing_ok=True)
    
    await state.clear()