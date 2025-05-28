import pendulum

from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.states import ScanURLStates
from services.check_url import check_url
from core.handlers.commands import router

current_prompts = []

TEMPLATE = """
🌐 <b>URL:</b> <i>{url}</i> 
🔒 <b>Status:</b> <i>{status}</i>  
⚠️ <b>Threats Detected:</b> <i>{threats}</i>    
"""

async def get_template_response(report):
    threat_found, threat_report = report

    if not threat_report:
        return "No link found in this message."
    
    output = "<b>Here's what I found about the link you sent.</b>\n\n"

    for url, threats in threat_report.items():
        status = "✅ Looks safe to me!" if not threats else "❌ Not safe!"
        threats_text = ",".join(threats) if threats else "None"

        output += TEMPLATE.format(url=url, status=status, threats=threats_text) + "\n\n"

    if threat_found:
        now = pendulum.now("UTC").format("YYYY-MM-DD HH:mm:ss")
        output += f"⏰ <b>Scanned on:</b> <i>{now}</i>"

    else:
        output = "✅ Looks safe to me!"

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
    