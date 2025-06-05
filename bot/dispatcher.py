from aiogram import Dispatcher
from core.handlers import commands 
from core.handlers.callbacks import callbacks

def register_handlers(dp: Dispatcher):
    dp.include_routers(
        commands.router,
        callbacks.router
    )