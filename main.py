import os
import asyncio
import aiohttp

from dotenv import find_dotenv, load_dotenv
from aiogram import Bot, Dispatcher, types

from bot.сommands.bot_command_list import user, admin
from bot.handlers.user_private import user_private_router
from bot.handlers.admin_private import admin_router
from sqlalchemy.ext.asyncio import AsyncSession

load_dotenv(find_dotenv())

from bot.middlewares.db import DataBaseSession
from bot.database.engine import session_maker, drop_db, create_db
from bot.database.orm_query import orm_get_apps

bot = Bot(token=os.getenv('TOKEN'))
bot.my_admins_list = [361467867]

dp = Dispatcher()

dp.include_router(admin_router)
dp.include_router(user_private_router)


async def on_startup(bot):
    run_param = False
    if run_param:
        await drop_db()

    await create_db()


async def on_shutdown(bot):
    print('бот лег')


async def get_requests(session: AsyncSession):
    data = await orm_get_apps(session)
    for app in data:
        async with aiohttp.ClientSession() as cs:
            async with cs.get(app.url) as resp:
                status_code = resp.status
                print(status_code)
    # while True:
    #     await asyncio.sleep()


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())
    await bot.set_my_commands(commands=user, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


asyncio.run(main())
