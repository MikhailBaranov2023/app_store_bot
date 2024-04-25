from aiogram.types import BotCommand

user = [
    BotCommand(command='menu', description='главное меню'),
    BotCommand(command='status', description='статус'),
    BotCommand(command='subscribe', description='подписатьтся'),
    BotCommand(command='getlaunchlinks', description='получить ссылку на приложение'),
]

admin = [
    BotCommand(command='add', description='добавить приложение'),
    BotCommand(command='remove', description='удалить приложение'),
    BotCommand(command='setinterval', description='установить интервал проверки доступности'),
    BotCommand(command='generatekey', description='сгенирировать ключ пользователя'),
    BotCommand(command='broadcast', description='отправка сообщения пользователям'),
]
