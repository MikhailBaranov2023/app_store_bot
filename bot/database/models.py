from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, backref
from sqlalchemy import String, Column, ForeignKey, BigInteger


class Base(DeclarativeBase):
    pass


class Application(Base):
    __tablename__ = 'application'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    open_url: Mapped[str] = mapped_column(String(150), unique=True, nullable=True)
    fail_count: Mapped[int] = mapped_column(nullable=True, default=0)


class Token(Base):
    __tablename__ = 'token'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    token: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)


class User(Base):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    token_id = Column(BigInteger, ForeignKey(Token.id))
    token = relationship('Token', uselist=False, backref=backref('user', uselist=False))
    user_name: Mapped[str] = mapped_column(unique=True, nullable=True, default='нет username')
