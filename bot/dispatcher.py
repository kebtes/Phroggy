from aiogram import Dispatcher
from core.handlers import commands 
from core.handlers.callbacks import callbacks
from core.handlers import message_listner

def register_handlers(dp: Dispatcher):
    dp.include_routers(
        commands.router,
        callbacks.router,
        message_listner.router
    )