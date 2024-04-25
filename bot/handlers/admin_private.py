import asyncio
from aiogram import types, Router, F
from aiogram.filters import CommandStart, or_f, Command, StateFilter
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.reply import admin_kb, user_kb
from bot.keyboards.inline import get_call_btns_for_delete
from bot.database.orm_query import orm_add_app, orm_get_apps, orm_delete_app, orm_create_token, orm_update_app, \
    orm_get_users
from src.requests_func import get_request
from src.genarate_token import gen_token

admin_router = Router()
admin_list = []


@admin_router.message(CommandStart())
async def start_cmd(message: types.Message, bot: Bot):
    if message.from_user.id in bot.my_admins_list:
        await message.answer(
            f"Привет, {message.from_user.first_name}. Вот панель администратора.",
            reply_markup=admin_kb)

    else:
        await message.answer(
            f"Привет, {message.from_user.first_name}. Этот бот показывает статус доступности приложений в App Store.",
            reply_markup=user_kb)


class AddAppUrl(StatesGroup):
    url = State()
    name = State()
    open_url = State()

    texts = {
        'AddAppUrl:url': 'Введите ссылку заново',
        'AddAppUrl:name': 'Введите название заново ',
    }


@admin_router.message(or_f(Command('add'), (F.text == 'Добавить приложение')), StateFilter(None))
async def app_list(message: types.Message, state: FSMContext):
    await message.answer('Введите ссылку на приложение', reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddAppUrl.url)


@admin_router.message(StateFilter('*'), Command('отмена'))
@admin_router.message(StateFilter('*'), F.text.casefold() == 'отмена')
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return None
    else:
        await state.clear()
    await message.answer('Действия отменены', reply_markup=admin_kb)


@admin_router.message(StateFilter('*'), Command('назад'))
@admin_router.message(StateFilter('*'), F.text.casefold() == 'назад')
async def step_back(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state == AddAppUrl.url:
        await message.answer('Предыдущего шага нет, введите ссылку на приложения либо введите "отмена"')
        return None
    previous = None
    for step in AddAppUrl.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(f'Вы вернулись к прошлому шагу\n {AddAppUrl.texts[previous.state]}')
            return None
        else:
            previous = step


@admin_router.message(AddAppUrl.url, F.text)
async def add_url(message: types.Message, state: FSMContext):
    await state.update_data(url=message.text)
    await message.answer('Введите название приложения')
    await state.set_state(AddAppUrl.name)


@admin_router.message(AddAppUrl.name, F.text)
async def add_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('Введите ссылку для запуска')
    await state.set_state(AddAppUrl.open_url)


@admin_router.message(AddAppUrl.open_url, F.text)
async def add_open_url(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.update_data(open_url=message.text)
    data = await state.get_data()
    try:
        if await get_request(data['url']) == 200:
            await orm_add_app(session=session, data=data)
            await message.answer('Приложение добавлено', reply_markup=admin_kb)
            await state.clear()
        else:
            await message.answer('Ссылка на приложение не активна, проверьте ссылку и добавьте новую',
                                 reply_markup=admin_kb)
            await state.clear()

    except Exception as e:
        await message.answer('При добавление произошла ошибка, попробуйте позже', reply_markup=admin_kb)
        await state.clear()


@admin_router.message(or_f(Command('remove'), (F.text == 'Удалить приложениие')))
async def app_list(message: types.Message, session: AsyncSession):
    data = await orm_get_apps(session)
    await message.answer('Выберите приложение которое хотите удалить',
                         reply_markup=get_call_btns_for_delete(sizes=(1,), data=data))


@admin_router.callback_query(F.data.startswith('delete_'))
async def delete_app(callback: types.CallbackQuery, session: AsyncSession):
    app_id = callback.data.split('_')[-1]
    await orm_delete_app(session=session, app_id=int(app_id))
    await callback.answer('Приложение удалено')
    await callback.message.answer('Приложение удалено')


class AddMinutes(StatesGroup):
    minutes = State()


@admin_router.message(or_f(Command('setinterval'), (F.text == 'Установить интервал')), StateFilter(None))
async def setting_interval(message: types.Message, state: FSMContext):
    await message.answer('Введите интервал проверки в минутах')
    await state.set_state(AddMinutes.minutes)


@admin_router.message(AddMinutes.minutes, F.text)
async def add_min(message: types.Message, session: AsyncSession, state: FSMContext, bot: Bot):
    await state.update_data(minutes=message.text)
    data = await state.get_data()
    await state.clear()
    minutes = data['minutes']
    while True:
        count = 0
        data = await orm_get_apps(session)
        for app in data:
            if await get_request(app.url) == 200:
                count += 1
                continue
            else:
                if app.fail_count == 3:
                    users = await orm_get_users(session)
                    for user in users:
                        try:
                            await bot.send_message(chat_id=user.chat_id,
                                                   text=f'Приложение {app.name} больше не доступно')
                            print('Уведомления отправлены')
                        except Exception as e:
                            print('не получилось отправить уведомление')
                            continue
                    await orm_delete_app(session, app_id=app.id)
                else:
                    fails = app.fail_count
                    new_fails = fails + 1
                    await orm_update_app(session, app.id, new_fails)
                    print('Ссылка не доступна меньше 3 раз, неудачная попытка зафиксирована')
                    count += 1
        await asyncio.sleep(int(minutes) * 10)


@admin_router.message(or_f(Command('generatekey'), (F.text == 'Сгенерировать ключ')))
async def gen_key(message: types.Message, session: AsyncSession):
    try:
        token = await gen_token()
        await orm_create_token(session=session, token=token)
        await message.answer(f'Ключ создан. Ключ - {token} ')

    except Exception as e:
        await message.answer('Что то пошло не так. Попробуйте позже', reply_markup=admin_kb)


class Message(StatesGroup):
    massage = State()


@admin_router.message(or_f(Command('broadcast'), (F.text == 'Отправить уведомление')), StateFilter(None))
async def app_list(message: types.Message, state: FSMContext):
    await message.answer('Введите сообщение для пользователей')
    await state.set_state(Message.massage)


@admin_router.message(Message.massage, F.text)
async def send_message(message: types.Message, session: AsyncSession, state: FSMContext, bot: Bot):
    await state.update_data(massage=message.text)
    data = await state.get_data()
    print(data['massage'])
    await state.clear()
    users = await orm_get_users(session)
    for user in users:
        try:
            await bot.send_message(chat_id=user.chat_id, text=data['massage'])
        except Exception as e:
            continue
    await message.answer('Сообщения отправлены')
