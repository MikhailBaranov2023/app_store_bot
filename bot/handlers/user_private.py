from aiogram import types, Router, F
from aiogram.filters import or_f, Command, StateFilter

from bot.database.orm_query import orm_get_apps, orm_get_app, orm_add_user, get_all_tokens, check_token, orm_check_user
from bot.keyboards.reply import user_kb
from sqlalchemy.ext.asyncio import AsyncSession
from bot.keyboards.inline import get_call_btns_get_app

user_private_router = Router()


@user_private_router.message(or_f(Command('menu'), (F.text.lower() == 'меню')))
async def app_list(message: types.Message):
    await message.answer('Вот меню', reply_markup=user_kb)


@user_private_router.message(or_f(Command('status'), (F.text == 'Список приложений')))
async def app_list(message: types.Message, session: AsyncSession):
    data = await orm_get_apps(session)
    if data == []:
        await message.answer('Пока нет доступных приложений')
    else:
        for app in data:
            await message.answer(f"{app.name}\nВот ссылка на приложение-{app.open_url}",
                                 reply_markup=user_kb)


@user_private_router.message(or_f(Command('getlaunchlinks'), (F.text == 'Сформировать ссылку для запуска')))
async def app_list(message: types.Message, session: AsyncSession):
    data = await orm_get_apps(session)
    if data == []:
        await message.answer('Пока нет доступных приложений')
    else:
        await message.answer('Выберите приложение для генерации ссылки',
                             reply_markup=get_call_btns_get_app(sizes=(1,), data=data))


@user_private_router.callback_query(F.data.startswith('get_'))
async def delete_app(callback: types.CallbackQuery, session: AsyncSession):
    app_id = callback.data.split('_')[-1]
    app = await orm_get_app(session=session, app_id=int(app_id))

    await callback.answer('Вот ссылка')
    await callback.message.answer(f"Ссылка для запуска{app.name}:{app.open_url}",
                                  reply_markup=user_kb)


@user_private_router.message(or_f(Command('subscribe'), (F.text == 'Подписаться')), StateFilter(None))
async def app_list(message: types.Message, session: AsyncSession):
    user_name = message.from_user.username
    chat_id = message.from_user.id
    tokens = await get_all_tokens(session=session)
    try:
        if await orm_check_user(session, chat_id=chat_id) is None:
            free_tokens = 0
            for token in tokens:
                if await check_token(session, token=token.id) is None:
                    free_tokens += 1
            if free_tokens > 0:
                for token in tokens:
                    if await check_token(session, token=token.id) is None:
                        user_token_id = token.id
                        if user_name is None:
                            await orm_add_user(session, chat_id=chat_id, user_name='нет username', token=token,
                                               token_id=user_token_id)
                        else:
                            await orm_add_user(session, user_name=user_name, chat_id=chat_id, token=token,
                                               token_id=user_token_id)
                        await message.answer('Вы подписаны')
                        break
                    else:
                        continue
            else:
                await message.answer('Нет доступных ключей, обратитесь к администратору')
        else:
            await message.answer('Вы уже подписаны')
    except Exception as e:
        await message.answer('Что то пошло не так. Попробуйте позже', reply_markup=user_kb)
