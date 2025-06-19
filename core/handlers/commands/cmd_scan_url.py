import pendulum
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.states import ScanURLStates
from core.handlers.commands import router
from services.check_url import check_url

current_prompts = []

async def get_template_response(report):
    TEMPLATE = (
        "{url}\n\n"
        "<u><b>📌Results</b></u>\n"
        "<b>Result:</b> {result}\n"
        "<b>Detected Threats:</b> {threats_found}\n"
        "<b>Date Scanned:</b> {date_scanned}\n\n"
        "<b><i>{footer}</i></b>"
    )

    threat_found, threat_report = report

    if not threat_report:
        return "No link found in this message."

    res = "Malicious" if threat_found else "No Threats Found"

    for url, threats in threat_report.items():
        capitalized = [threat.capitalize() for threat in threats]
        threats_text = ",".join(capitalized) if threats else "None"

    now = pendulum.now("UTC").format("YYYY-MM-DD HH:mm:ss")

    FOOTER_1 = "<b><i>This link appears to be unsafe and could potentially harm your device or compromise your personal information. For your safety, please refrain from clicking on it or sharing it with others.</i></b>"
    FOOTER_2 = "<b><i>No suspicious content was found in this link. It appears safe for now, but please remain cautious when interacting with unfamiliar links.</i></b>"

    output = TEMPLATE.format(
        url          = url,
        result       = res,
        threats_found = threats_text,
        footer       = FOOTER_1 if res == "Malicious" else FOOTER_2,
        date_scanned = now
    )

    return output.strip()

@router.message(Command("scan_url"))
async def ask_for_url(message: types.Message, state: FSMContext):
    global current_prompts

    prompt = await message.answer("Please forward the message containing the URL you'd like me to scan.")
    await state.set_state(ScanURLStates.waiting_for_url)

    current_prompts.extend([prompt.message_id, message.message_id])

@router.message(ScanURLStates.waiting_for_url)
async def handle_url(message: types.Message, state: FSMContext):
    report = await check_url(message.text)
    report_msg = await get_template_response(report)

    global current_prompts
    for id in current_prompts:
        await message.bot.delete_message(message.chat.id, id)
    current_prompts = []

    await message.reply(report_msg)
    await state.clear()
