from aiogram.fsm.state import State, StatesGroup

class ScanFileStates(StatesGroup):
    waiting_for_file = State()

class ScanURLStates(StatesGroup):
    waiting_for_url = State()