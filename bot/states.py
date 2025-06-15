from aiogram.fsm.state import State, StatesGroup


class ScanFileStates(StatesGroup):
    waiting_for_file = State()

class ScanURLStates(StatesGroup):
    waiting_for_url = State()

class AddToGroupStates(StatesGroup):
    waiting_for_id = State()

class MyGroupStates(StatesGroup):
    group_listing = State()
    waiting_for_group_choice = State()
    waiting_for_actions = State()
    waiting_approval_group_deletion = State()

class HelpStates(StatesGroup):
    main = State()
    group_settings = State()
    automation_filtering = State()
    moderation_controls = State()
    detection_sensitivity = State()
    logs = State()