from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

user_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Список приложений'),
            KeyboardButton(text='Сформировать ссылку для запуска'),
        ],
        [
            KeyboardButton(text='Подписаться')
        ],
        [
            KeyboardButton(text='FAQ'),
        ]
    ], resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню'
)

admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Добавить приложение'),
            KeyboardButton(text='Удалить приложениие'),
        ],
        [
            KeyboardButton(text='Установить интервал'),
            KeyboardButton(text='Сгенерировать ключ'),
        ],
        [
            KeyboardButton(text='Отправить уведомление')
        ]
    ], resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню админимтратора'
)

delete_kb = ReplyKeyboardRemove()
