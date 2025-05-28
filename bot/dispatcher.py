from aiogram import Dispatcher
from core.handlers.commands import router

def register_handlers(dp: Dispatcher):
    dp.include_router(router)