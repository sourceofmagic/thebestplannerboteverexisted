from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from datetime import date

import app.keyboards as kb
import app.database.requests as rq

router = Router()
class Addtask(StatesGroup):
    task = State()
    deadline = State()
    comm = State()
    uid = State()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
        await state.set_state(Addtask.uid)
        await state.update_data(uid=message.from_user.id)
        await message.reply(f'Привет, {message.from_user.first_name}! \nЭто бот, который поможет тебе делать дела вовремя. Я буду присылать тебе список твоих задач, чтобы ты не расслаблялся. Просто пришли свою задачу и срок, до которого её нужно осилить.\nДерзай, йоу!',
                             reply_markup=kb.main_inline)


@router.message(Command('help'))
async def get_help(message: Message):
    await message.reply_photo(photo='https://avatars.mds.yandex.net/i?id=f17d60d6dddce43b688ab84fa37dd024_l-5581032-images-thumbs&n=13',
                              caption="СПИСОК КОМАНД\n\n/registration - начало работы с ботом\n/help - помощь\n/start - что делает этот бот")

@router.message(F.text == 'Как дела?')
async def how_are_you(message: Message):
    await message.reply_photo(photo="https://avatars.mds.yandex.net/i?id=b63ee5a719a37e17384ecc4af94b0628_l-5858269-images-thumbs&n=13",
                              caption="Самое время начать работать, чувак!")

# СПИСОК ЗАДАЧ

@router.callback_query(F.data == 'show_tasks_list')
async def show_tasks_list(callback: CallbackQuery):
    await callback.answer('')
    tasks = await rq.get_tasks(callback.from_user.id)
    ans = ["ТВОИ ЗАДАЧИ: "]
    i=0
    for t in tasks:
        i+=1
        ans.append(f"\n\n{i}. {t.task}\nОСТАЛОСЬ ДНЕЙ: {await time_left(t.data)}\nКомментарий: {t.comm}")
    if len(ans)>1:
        await callback.message.edit_text("\n".join(ans),
                                     reply_markup=kb.list_inline)
    else:
        await callback.message.edit_text('Нет задач, самое время их добавить!',
                                         reply_markup=kb.error_add_inline)


#УДАЛЕНИЕ ЗАДАЧИ


@router.callback_query(F.data == 'del_task')
async def delete_task_start(callback: CallbackQuery):
    await callback.answer('')
    tasks = await rq.get_tasks(callback.from_user.id)
    if tasks.first() is not None:
        await callback.message.edit_text('Выберите задачу для удаления',
                                     reply_markup=await kb.del_task_kb(tasks))
    else:
        await callback.message.edit_text('Нет доступных для удаления задач, самое время их добавить!',
                                         reply_markup=kb.error_add_inline)


@router.callback_query(F.data.startswith('task_'))
async def delete_task_end(callback: CallbackQuery):
    await callback.answer('')
    try:
        task_id=callback.data.split('_')[-1]
        await rq.del_task(task_id)
        await callback.message.edit_text('Задача успешно удалена!',
                                         reply_markup=kb.main_inline)
        #print(task_id)
    except Exception as e:
        await callback.message.edit_text(
            f"Ошибка \n{str(e)}"
        )


# ДОБАВЛЕНИЕ ЗАДАЧИ

@router.callback_query(F.data == 'add_task')
async def reg_one(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Addtask.task)
    await callback.message.edit_text('Введите задачу')

@router.message(Addtask.task)
async def reg_two(message: Message, state: FSMContext):
    await state.update_data(uid=message.from_user.id)
    if len(message.text) >= 150:
        await message.answer('Название задачи превышает 150 символов. Попробуйте заново.',
                             reply_markup=kb.error_add_inline)
    else:
        await state.update_data(task=message.text)
        await state.set_state(Addtask.deadline)
        await message.answer('Введите срок сдачи в формате дд.мм.гггг, иначе все пойдет по жопе')

@router.message(Addtask.deadline)
async def reg_three(message: Message, state: FSMContext):
    try:
        await state.update_data(deadline=await to_date(message.text))
        await state.set_state(Addtask.comm)
        await message.answer('Введите комментарий к задаче')
    except ValueError as e:
        await message.answer(str(e), reply_markup=kb.error_add_inline)

@router.message(Addtask.comm)
async def two_three(message: Message, state: FSMContext):
    if len(message.text) >= 500:
        await message.answer("Комментарий превышает 500 символов, попробуйте заново.",
                             reply_markup=kb.error_add_inline)
    else:
        await state.update_data(comm=message.text)
        tasks = await state.get_data()
        try:
            await rq.set_user(message.from_user.id, message.from_user.first_name)

            await rq.set_task(tasks)
            await message.answer(f'Задача успешно сохранена.\n\nЗадача: {tasks["task"]}\nОсталось дней: {await time_left(tasks["deadline"])}\nКомментарий: {tasks["comm"]}',
                                 reply_markup=kb.main_inline)

            await state.clear()
        except Exception as e:
            await message.answer(
                f"Ошибка сохранения\n{str(e)}",
                reply_markup=kb.error_add_inline
            )
            await state.clear()

# ФУНКЦИИ ДЛЯ РАБОТЫ С ДАТОЙ
async def to_date(ddl: str) -> date:
    try:
        day, month, year = map(int, ddl.split('.'))
        return date(year, month, day)
    except (ValueError, AttributeError) as e:
        raise ValueError(f"Неверный формат даты: {ddl}. Ожидается дд.мм.гггг. Попробуйте заново.") from e

async def time_left(ddl) -> int:
    if ddl is None:
        return None
    today = date.today()
    diff = ddl - today
    if diff.days == 1:
        return "ЗАВТРА ДЕДЛАЙН!"
    elif diff.days < 0:
        return "ПРОСРОЧЕНО"
    elif diff.days == 0:
        return "СЕГОДНЯ ДЕДЛАЙН"
    else:
        return diff.days



