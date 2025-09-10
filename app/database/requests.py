from app.database.models import async_session
from app.database.models import User, Task
from sqlalchemy import select, update, delete

from datetime import date
async def set_user(tg_id, name):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id, User.name == name))

        if not user:
            session.add(User(tg_id=tg_id, name=name))
            await session.commit()

async def set_task(tasks: dict):
    async with async_session() as session:
        t = await session.scalar(select(Task).where(Task.task == tasks["task"], Task.user_id == tasks["uid"]))
        if t:
            raise Exception("Такая задача уже существует.")
        else:
            session.add(Task(
                task=tasks["task"],
                data=tasks["deadline"],
                comm=tasks["comm"],
                user_id=tasks["uid"]
            ))
            await session.commit()

async def get_uid(tg_id):
    async with async_session() as session:
        return await session.scalar(select(User).where(User.tg_id == tg_id))

async def get_users_all():
    async with async_session() as session:
        return await session.scalars(select(User))

async def get_tasks(uid):
    async with async_session() as session:
        return await session.scalars(select(Task).where(Task.user_id == uid))

async def del_task(task_id):
    async with async_session() as session:
        await session.execute(delete(Task).where(Task.id == task_id))
        await session.commit()

async def del_user(uid):
    async with async_session() as session:
        try:
            await session.execute(delete(Task).where(Task.user_id == uid))
            await session.execute(delete(User).where(User.tg_id == uid))
            await session.commit()
        except Exception as e:
            print(str(e))