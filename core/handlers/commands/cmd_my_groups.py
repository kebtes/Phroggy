"""

This command should handle

- list all linked groups by the user
- for each listed group
    - group removal/unlink      : group should be removed from db
    - ability to change admin   : should prompt the user to be sure
    - ability to get log history for each : (this can wait till log history is fully impl) 

"""

from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.states import MyGroupStates
from core.handlers.commands import router
from core.keyboards import create
from db import groups, users


@router.message(Command("my_groups"))
async def list_groups(message: types.Message, state: FSMContext):
    user_id = message.chat.id
    user_groups = await users.get_groups(user_id)

    if user_groups:
        buttons = []
        for group_id in user_groups:
            info = await groups.group_info(group_id)
            group_name = info.get("group_name") if info else None
            group_id = info.get("group_id") if info else None
            if group_name:
                buttons.append([group_name, f"info:group:{group_id}"])

        reply_markup = create(
            buttons=buttons,
            per_row=2
        )

        response_msg = (
            "Below is a list of all the groups you've added me to. "
            "Tap on any group to either unlink it or update its admin settings."
        )

        await message.answer(response_msg, reply_markup=reply_markup)
        await state.set_state(MyGroupStates.waiting_for_group_choice)

    else:
        response_msg = (
            "Looks like you haven't added me to any groups yet!\n\n"
            "Use /link_group to get started."
        )

        await message.reply(response_msg)
