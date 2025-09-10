import asyncio
import logging

from aiogram import Bot, Dispatcher
from app.handlers import router
from dotenv import load_dotenv
import os
from app.database.models import async_main
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.database.requests import get_users_all, get_tasks, del_user
from app.handlers import time_left

from keep_alive import keep_alive

load_dotenv()
bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(bot=bot)

async def main():
    await async_main()
    keep_alive()
    dp.include_router(router)

    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(
        everyday_reminder,
        CronTrigger(hour=6, minute=0),
        kwargs={"bot": bot}
    )
    scheduler.start()

    await dp.start_polling(bot)

# ЕЖЕДНЕВНОЕ СООБЩЕНИЕ ОТ БОТА

async def everyday_reminder(bot: Bot):
    users = await get_users_all()
    for u in users:
        tasks = await get_tasks(u.tg_id)
        ans = [f"Доброе утро, {u.name}!\nТвои задачи на сегодня: "]
        i = 0
        for t in tasks:
            i+=1
            ans.append(f"\n\n{i}. {t.task}\nОСТАЛОСЬ ДНЕЙ: {await time_left(t.data)}\nКомментарий: {t.comm}")
        try:
            if len(ans) > 1:
                await bot.send_message(u.tg_id, f"\n".join(ans))
            else:
                await bot.send_message(u.tg_id, 'Нет задач, самое время их добавить!')
        except (TelegramBadRequest, TelegramForbiddenError) as e:
            print(f"Чат с пользователем {u.tg_id} недоступен по причине {str(e)}")
            await del_user(u.tg_id)



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

