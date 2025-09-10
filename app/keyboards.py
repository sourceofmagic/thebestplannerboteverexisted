from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# main_reply = ReplyKeyboardMarkup(
#     keyboard=[
#         [KeyboardButton(text='Список задач')],
#         [KeyboardButton(text='Добавить новую задачу'), KeyboardButton(text='Удалить задачу')]
#     ],
#     resize_keyboard=True,
#     input_field_placeholder='Выберите пункт меню'
# )

# КЛАВИАТУРА НА СТАРТЕ

main_inline = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='Список задач', callback_data='show_tasks_list')],
                     [InlineKeyboardButton(text='Добавить задачу', callback_data='add_task'),
                      InlineKeyboardButton(text='Удалить задачу', callback_data='del_task')]
                     ]
)

# Клавиатура под списком задач

list_inline = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='Добавить задачу', callback_data='add_task'),
                      InlineKeyboardButton(text='Удалить задачу', callback_data='del_task')]
                     ]
)

# Клавиатура если не удалось добавить задачу, либо задач нет

error_add_inline = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='Добавить задачу', callback_data='add_task')]
                     ]
)

#КЛАВИАТУРА ДЛЯ УДАЛЕНИЯ ЗАДАЧИ

async def del_task_kb(tasks):
    keyboard = InlineKeyboardBuilder()
    for t in tasks:
        keyboard.add(InlineKeyboardButton(text=t.task, callback_data=f'task_{t.id}'))
    return keyboard.adjust(2).as_markup()
