from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update

from bot.database.models import Application, User, Token


async def orm_add_app(session: AsyncSession, data: dict):
    obj = Application(
        url=data['url'],
        name=data['name'],
        open_url=data['open_url']
    )
    session.add(obj)
    await session.commit()


async def orm_update_app(session: AsyncSession, app_id: int, fail: int):
    query = update(Application).where(Application.id == app_id).values(
        fail_count=fail
    )
    await session.execute(query)
    await session.commit()


async def orm_get_apps(session: AsyncSession):
    query = select(Application)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_app(session: AsyncSession, app_id: int):
    query = select(Application).where(Application.id == app_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_delete_app(session: AsyncSession, app_id):
    query = delete(Application).where(Application.id == app_id)
    await session.execute(query)
    await session.commit()


async def orm_get_users(session: AsyncSession):
    query = select(User)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_add_user(session: AsyncSession, chat_id: int, user_name: str, token: Token, token_id: Token.id):
    obj = User(
        chat_id=chat_id,
        user_name=user_name,
        token=token,
        token_id=token_id
    )
    session.add(obj)
    await session.commit()


async def orm_check_user(session: AsyncSession, chat_id: int):
    query = select(User).where(User.chat_id == chat_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_create_token(session: AsyncSession, token):
    obj = Token(
        token=token
    )
    session.add(obj)
    await session.commit()


async def get_all_tokens(session: AsyncSession):
    query = select(Token)
    result = await session.execute(query)
    return result.scalars().all()


async def check_token(session: AsyncSession, token):
    query = select(User).where(User.token_id == token)
    result = await session.execute(query)
    return result.scalar()
