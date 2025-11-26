from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup,InlineKeyboardButton, ReplyKeyboardRemove
from bot.loader import _

choose_language = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [   
                InlineKeyboardButton(text="🇺🇦Україньска", callback_data="lang_uk"),
                InlineKeyboardButton(text="Русский", callback_data="lang_ru")
            ],
            [
                InlineKeyboardButton(text="🇬🇧English", callback_data="lang_en"),
                InlineKeyboardButton(text="🇩🇪Deutsch", callback_data="lang_de")
                
            ]
        ]
    )

choose_car_body = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [   
                InlineKeyboardButton(text=_("Седан"), callback_data="Седан")
            ],
            [   
                InlineKeyboardButton(text=_("Универсал"), callback_data="Универсал")
            ],
            [   
                InlineKeyboardButton(text=_("Хечбек"), callback_data="Хечбек")
            ],
            [   
                InlineKeyboardButton(text=_("Внедорожник/Кроссовер"), callback_data="Внедорожник/Кроссовер")
            ],
            [   
                InlineKeyboardButton(text=_("Купе"), callback_data="Купе")
            ],
            [   
                InlineKeyboardButton(text=_("Кабриолет"), callback_data="Кабриолет")
            ],
            [   
                InlineKeyboardButton(text=_("Минивен"), callback_data="Минивен")
            ],
            [   
                InlineKeyboardButton(text=_("Пикап"), callback_data="Пикап")
            ],
            [
                InlineKeyboardButton(text=_("Лимузин"), callback_data="Лимузин")
            ],
            [
                InlineKeyboardButton(text=_("Микроавтобус"), callback_data="Микроавтобус")
            ],
            [
                InlineKeyboardButton(text=_("⬅️ Назад"), callback_data="cancel")
            ]
        ]
    )

choose_fuel_type = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [   
                InlineKeyboardButton(text=_("Бензин"), callback_data=_("Бензин"))
            ],
            [   
                InlineKeyboardButton(text=_("Дизель"), callback_data=_("Дизель"))
            ],
            [   
                InlineKeyboardButton(text=_("Электро"), callback_data=_("Электро"))
            ],
            [   
                InlineKeyboardButton(text=_("Гибрид"), callback_data=_("Гибрид"))
            ],
            [   
                InlineKeyboardButton(text=_("Газ/Бензин"), callback_data=_("Газ/Бензин"))
            ],
            [   
                InlineKeyboardButton(text=_("⬅️ Назад"), callback_data="cancel")
            ],
        ]
    )

choose_registration = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [   
                InlineKeyboardButton(text=_("Германия"), callback_data="Германия")
            ],
            [   
                InlineKeyboardButton(text=_("Украина"), callback_data="Украина")
            ],
            [   
                InlineKeyboardButton(text=_("ЕС"), callback_data="ЕС")
            ],
            [   
                InlineKeyboardButton(text=_("⬅️ Назад"), callback_data="cancel")
            ],
        ]
    )

choose_new_language = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [   
                InlineKeyboardButton(text="🇺🇦Україньска", callback_data="new_lang_uk"),
                InlineKeyboardButton(text="Русский", callback_data="new_lang_ru")
            ],
            [
                InlineKeyboardButton(text="🇬🇧English", callback_data="new_lang_en"),
                InlineKeyboardButton(text="🇩🇪Deutsch", callback_data="new_lang_de")
                
            ]
        ]
    )

def get_tel_number(lang):
    send_tel_number_markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=_("Отправить номер", locale=lang), request_contact=True)
            ]
        ],
        resize_keyboard=True
    )
    return send_tel_number_markup

user_main_menu_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=_("Создать объявление 🆕"))
        ],
        [
            KeyboardButton(text=_("Настройки ⚙️")),
            KeyboardButton(text=_("Мои объявления"))
        ]
        
    ],
    resize_keyboard=True
)

select_article_type_markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=_("❗️ Продам"))
            ],
            [
                KeyboardButton(text=_("↔️ Обмен")),
                KeyboardButton(text=_("❓ Куплю"))
            ],
            [
                KeyboardButton(text=_("❌ Отменить"))
            ]

        ],
        resize_keyboard=True
    )
# def get_create_article_default_markup()
create_article_default_markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=_("Пропустить ➡️")),
                
            ],
            [
                KeyboardButton(text=_("⬅️ Назад")),
                KeyboardButton(text=_("❌ Отменить"))
            ]
        ],
        resize_keyboard=True
    )

tuf_markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=_("Без тюфа")),
                
            ],
            [
                KeyboardButton(text=_("⬅️ Назад")),
                KeyboardButton(text=_("❌ Отменить"))
            ]
        ],
        resize_keyboard=True
    )

geoposition_markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=_("Отправить местоположение 📍"),request_location=True)
            ],
            [
                KeyboardButton(text=_("⬅️ Назад")),
                KeyboardButton(text=_("Пропустить ➡️")),
                KeyboardButton(text=_("❌ Отменить"))
            ]
        ],
        resize_keyboard=True
    )

accept_create_article = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=_("Да")),
                KeyboardButton(text=_("Нет"))
            ]
        ],
        resize_keyboard=True
    )

user_settings_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=_("Язык")),
            # KeyboardButton(text=_("Номер телефона"))
        ],
        [
            KeyboardButton(text=_("❌ Отменить"))
        ]
    ],
    resize_keyboard=True
)
