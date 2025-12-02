import asyncio
from datetime import datetime
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery,BotCommand, photo_size, ContentTypes, ContentType, ReplyKeyboardRemove, InputMediaPhoto, MediaGroup
from aiogram.dispatcher.filters import CommandStart, Text, MediaGroupFilter
# from aiogram.dispatcher.filters import F
from typing import List
import json 
import re
import pickle
import jsonpickle

from bot.keyboards.user_keyboards import choose_language, get_tel_number, user_main_menu_markup, select_article_type_markup, create_article_default_markup, accept_create_article, choose_new_language, choose_car_body, choose_fuel_type, choose_registration, tuf_markup, gearbox_type_button
from bot.keyboards.admin_keyboard import admin_main_menu_markup, get_lang_markup
from bot.states.states import CreateArticleStates, ModerationStates, RegistrationStates
from bot.database.database import Article, DBCommands, User, DuplicateArticleException
from bot.loader import dp, bot, _
from bot.config import ADMIN_ID
from bot.utils.misc import rate_limit
from bot.utils.utils import get_sample_from_article, send_article_to_chanel, check_article_for_errors, redis_client, set_last_moderation_time
import logging


logger = logging.getLogger('user_handler')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="bot/logs/user_handler.log")
formatter = logging.Formatter('[%(asctime)s] - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


db = DBCommands()

async def register_commands():
    await bot.set_my_commands([
        BotCommand('restart', 'Рестарт')
    ])
    
@rate_limit(5)
@dp.message_handler(commands="start")
@dp.message_handler(commands="restart", state="*")
async def __start(msg: Message, state: FSMContext) -> None:
    await state.reset_data()
    await state.reset_state()
    user_id = msg.from_user.id
    user_name = msg.from_user.full_name
    await bot.send_sticker(msg.from_user.id, sticker="CAACAgIAAxkBAAIJQWSO2SepS6soZ_x0oaMce-r6Vd4QAAJxDgACHIJQS-TTUGYws97lLwQ")
    await msg.bot.send_message(user_id, f'Привет, {user_name}!', reply_markup=ReplyKeyboardRemove())
    await db.add_new_user()
    await msg.bot.send_message(user_id, "Выбери язык", reply_markup=choose_language)

@dp.callback_query_handler(text_contains="lang")
async def __set_language(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    # Достаем последние 2 символа (например ru)
    lang = call.data[-2:]
    user: User  = await db.set_language(lang)
    data = await state.get_data()
    is_edit = data.get('change_language')
    await call.message.answer(_("Ваш язык был изменен", locale=lang), reply_markup= get_lang_markup(lang, call))
    if is_edit:
        await bot.send_message(call.from_user.id, _("Выберите следущее действие", locale=lang), reply_markup= get_lang_markup(lang, call))
    await state.reset_data()
    if not is_edit:
        # if user.mobile:
        # После того, как мы поменяли язык, в этой функции все еще указан старый, поэтому передаем locale=lang
            
        await bot.send_message(call.from_user.id, _("Добро пожаловать в главное меню!", locale=lang), reply_markup=get_lang_markup(lang, call))
        # else:
        #     await bot.send_message(call.from_user.id, _('Отправьте свой номер телефона', locale=lang), reply_markup=get_tel_number(lang))
        #     await RegistrationStates.NUMBER.set()
    await call.answer()

@dp.message_handler(content_types=ContentTypes.CONTACT | ContentTypes.TEXT, state=RegistrationStates.NUMBER)
async def __set_number(msg: Message, state: FSMContext):
    if 'contact' in msg:
        phone_number = msg['contact']['phone_number']
    else:
        phone_number = msg.text
        validate_phone_number_pattern = "^\\+?[0-9][0-9]{7,14}$"
        number  = re.match(validate_phone_number_pattern, msg.text)
        if not number: 
            await bot.send_message(msg.from_user.id, _('Неправильный формат номера, попробуй еще раз'))
            return
        
    data = await state.get_data()
    is_edit = data.get('change_number')

    await db.set_mobile(phone_number)
    if is_edit:
        await bot.send_message(msg.from_user.id, _("Номер телефона был изменен"), reply_markup=admin_main_menu_markup if str(msg.from_user.id) in ADMIN_ID else user_main_menu_markup)
    else:
        await bot.send_message(msg.from_user.id, _("Вы в главном меню! 🫡"), reply_markup=admin_main_menu_markup if str(msg.from_user.id) in ADMIN_ID else user_main_menu_markup)
    await state.reset_state()

# @dp.message_handler(state=CreateArticleStates.FINISHED)
@dp.message_handler(Text(equals=[_("❌ Отменить")]), state="*")
async def main_menu(msg: Message, state: FSMContext):
    cur_state = await state.get_state()
    # print(type(cur_state))
    # print(cur_state)
    if cur_state == "ModerationStates:MODERATE":
        # print('qqqq')
        set_last_moderation_time()
    await bot.send_message(msg.from_user.id, _("Вы в главном меню!"), reply_markup=admin_main_menu_markup if str(msg.from_user.id) in ADMIN_ID else user_main_menu_markup)
    await state.reset_state()
    await state.reset_data()

@dp.message_handler(Text(equals=[_("⬅️ Назад")]), state=CreateArticleStates.MARKA)
@dp.message_handler(Text(equals=[_("Создать объявление 🆕")]))
async def __create_article(msg: Message, state: FSMContext):
    await bot.send_message(msg.from_user.id, _("Выберите категрию"), reply_markup=select_article_type_markup)
    await CreateArticleStates.CATEGORY.set()

@dp.message_handler(Text(equals=[_("⬅️ Назад")]), state=CreateArticleStates.MODEL)
@dp.message_handler(state=CreateArticleStates.CATEGORY)
async def __select_category(msg: Message, state: FSMContext):
    if msg.text != str(_("⬅️ Назад")) and msg.text in [str(_("❓ Куплю")), str(_("↔️ Обмен")), str(_("❗️ Продам"))]:
        article = Article()
        article.type = msg.text
    elif  msg.text == str(_("⬅️ Назад")):
        data = await state.get_data()
        article: Article = Article(**json.loads(jsonpickle.decode(data['article']))['__values__'])
    else:
        return

    article.user_id = msg.from_user.id
    await bot.send_message(msg.from_user.id, _("Введите марку авто"), reply_markup=create_article_default_markup)
    await CreateArticleStates.MARKA.set()
    await state.update_data(article=json.dumps(jsonpickle.encode(article, unpicklable=False)))

# @dp.message_handler(Text(equals=[_("⬅️ Назад")]), state=CreateArticleStates.MODEL)
# @dp.message_handler(state=CreateArticleStates.TITLE)
# async def __select_title(msg: Message, state: FSMContext):
#     data = await state.get_data()
#     article: Article = Article(**json.loads(jsonpickle.decode(data['article']))['__values__'])
#     article.title = msg.text.replace(str(_("Пропустить ➡️")), "").replace(str(_("⬅️ Назад")), "")
#     await bot.send_message(msg.from_user.id, _("Введите марку авто"), reply_markup=create_article_default_markup)
#     await CreateArticleStates.MARKA.set()
#     await state.update_data(article=json.dumps(jsonpickle.encode(article, unpicklable=False)))

@dp.message_handler(Text(equals=[_("⬅️ Назад")]), state=CreateArticleStates.YEAR)
@dp.message_handler(state=CreateArticleStates.MARKA)
async def __select_marka(msg: Message, state: FSMContext):
    data = await state.get_data()
    article: Article = Article(**json.loads(jsonpickle.decode(data['article']))['__values__'])
    article.marka = msg.text.replace(str(_("Пропустить ➡️")), "").replace(str(_("⬅️ Назад")), "")
    await bot.send_message(msg.from_user.id, _("Введите модель авто"), reply_markup=create_article_default_markup)
    await CreateArticleStates.MODEL.set()
    await state.update_data(article=json.dumps(jsonpickle.encode(article, unpicklable=False)))

@dp.message_handler(Text(equals=[_("⬅️ Назад")]), state=CreateArticleStates.GEARBOX_TYPE)
@dp.callback_query_handler(text_contains="cancel", state=CreateArticleStates.GEARBOX_TYPE)
@dp.message_handler(state=CreateArticleStates.MODEL)
async def __select_model(msg: Message | CallbackQuery, state: FSMContext):
    data = await state.get_data()
    article: Article = Article(**json.loads(jsonpickle.decode(data['article']))['__values__'])
    if isinstance(msg, Message):
        article.model = msg.text.replace(str(_("Пропустить ➡️")), "").replace(str(_("⬅️ Назад")), "")
    else: 
        await msg.message.delete()
    await bot.send_message(msg.from_user.id, _("Введите год авто"), reply_markup=create_article_default_markup)
    await CreateArticleStates.YEAR.set()
    await state.update_data(article=json.dumps(jsonpickle.encode(article, unpicklable=False)))

@dp.message_handler(Text(equals=[_("⬅️ Назад")]), state=CreateArticleStates.CAR_BODY)
@dp.callback_query_handler(text_contains="cancel", state=CreateArticleStates.CAR_BODY)
@dp.message_handler(state=CreateArticleStates.YEAR)
async def __select_year(msg: Message | CallbackQuery, state: FSMContext):
    data = await state.get_data()
    article: Article = Article(**json.loads(jsonpickle.decode(data['article']))['__values__'])
    print(type(msg))
    if isinstance(msg, Message):
        # await bot.send_message(msg.from_user.id, _("☑️☑️☑️"),reply_markup=ReplyKeyboardRemove())
        article.year = msg.text.replace(str(_("Пропустить ➡️")), "").replace(str(_("⬅️ Назад")), "")
    else:
        await msg.message.delete()
        article.year = str("").replace(str(_("Пропустить ➡️")), "").replace(str(_("⬅️ Назад")), "")
    await bot.send_message(msg.from_user.id, _("Выберите тип коробки"),  reply_markup=gearbox_type_button)
    await CreateArticleStates.GEARBOX_TYPE.set()
    await state.update_data(article=json.dumps(jsonpickle.encode(article, unpicklable=False)))

@dp.callback_query_handler(lambda callback: callback.data == "cancel", state=CreateArticleStates.ENGINE_TYPE)
@dp.message_handler(Text(equals=[_("⬅️ Назад")]), state=CreateArticleStates.ENGINE_TYPE)
@dp.message_handler(state=CreateArticleStates.GEARBOX_TYPE)
async def __select_gearbox_type(call: CallbackQuery | Message, state: FSMContext):
    if isinstance(call, Message):
        text = call.text
    else:
        if call.data == "cancel":
            text = ""
        else:
            text = call.data
        await call.message.delete()
    # await call.message.edit_reply_markup()
    if text not in [_("Автомат"), _("Механика")]:
        return
    await bot.send_message(call.from_user.id, _("☑️☑️☑️"),reply_markup=ReplyKeyboardRemove())
    data = await state.get_data()
    article: Article = Article(**json.loads(jsonpickle.decode(data['article']))['__values__'])
    article.gearbox_type = text.replace(str(_("Пропустить ➡️")), "").replace(str(_("⬅️ Назад")), "")
    await bot.send_message(call.from_user.id, _("Выберите кузов авто"),  reply_markup=choose_car_body)
    await CreateArticleStates.CAR_BODY.set()
    await state.update_data(article=json.dumps(jsonpickle.encode(article, unpicklable=False)))
    if isinstance(call, CallbackQuery):
        await call.answer()

@dp.message_handler(Text(equals=[_("⬅️ Назад")]), state=CreateArticleStates.ENGINE_CAPACITY)
@dp.callback_query_handler(state=CreateArticleStates.CAR_BODY)
async def __select_car_body(call: CallbackQuery | Message, state: FSMContext):
    if isinstance(call, Message):
        text = call.text
        await bot.send_message(call.from_user.id, _("☑️☑️☑️"),reply_markup=ReplyKeyboardRemove())
    else:
        if call.data == "cancel":
            text = ""
        else:
            text = call.data
        await call.message.delete()
    # await call.message.edit_reply_markup()
    data = await state.get_data()
    article: Article = Article(**json.loads(jsonpickle.decode(data['article']))['__values__'])
    article.body_type = text.replace(str(_("Пропустить ➡️")), "").replace(str(_("⬅️ Назад")), "")
    await bot.send_message(call.from_user.id, _("Выберите тип двигателя"), reply_markup=choose_fuel_type)
    await CreateArticleStates.ENGINE_TYPE.set()
    await state.update_data(article=json.dumps(jsonpickle.encode(article, unpicklable=False)))
    if isinstance(call, CallbackQuery):
        await call.answer()

@dp.message_handler(Text(equals=[_("⬅️ Назад")]), state=CreateArticleStates.TUF)
@dp.callback_query_handler(state=CreateArticleStates.ENGINE_TYPE)
async def __select_engine_type(call: CallbackQuery | Message, state: FSMContext):
    print(call)
    data = await state.get_data()
    if isinstance(call, CallbackQuery):
        await call.message.delete()
        if call.data == "cancel":
            text = ""
        else:
            text = call.data
    else:
        text = call.text
    # await call.message.edit_reply_markup()
    article: Article = Article(**json.loads(jsonpickle.decode(data['article']))['__values__'])
    article.engine_type = text.replace(str(_("Пропустить ➡️")), "").replace(str(_("⬅️ Назад")), "")
    await bot.send_message(call.from_user.id, _("Выберите обьем двигателя"), reply_markup=create_article_default_markup)
    await CreateArticleStates.ENGINE_CAPACITY.set()
    await state.update_data(article=json.dumps(jsonpickle.encode(article, unpicklable=False)))
    if isinstance(call, CallbackQuery):
        await call.answer()

@dp.callback_query_handler(lambda callback: callback.data == "cancel", state=CreateArticleStates.REGISTRATION)
@dp.message_handler(state=CreateArticleStates.ENGINE_CAPACITY)
async def __select_engine_capacity(msg: Message | CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if isinstance(msg, CallbackQuery):
        if msg.data == "cancel":
            text = ""
        else:
            text = msg.data
        await msg.message.delete()
    else:
        text = msg.text
    article: Article = Article(**json.loads(jsonpickle.decode(data['article']))['__values__'])
    article.engine_capacity = text.replace(str(_("Пропустить ➡️")), "").replace(str(_("⬅️ Назад")), "")
    await bot.send_message(msg.from_user.id, _("Тюф годен до: "), reply_markup=tuf_markup)
    await CreateArticleStates.TUF.set()
    await state.update_data(article=json.dumps(jsonpickle.encode(article, unpicklable=False)))
    if isinstance(msg, CallbackQuery):
        await msg.answer()

@dp.message_handler(Text(equals=[_("⬅️ Назад")]), state=CreateArticleStates.DESCRIPTION)
@dp.message_handler(state=CreateArticleStates.TUF)
async def __select_tuf(msg: Message, state: FSMContext):
    data = await state.get_data()
    article: Article = Article(**json.loads(jsonpickle.decode(data['article']))['__values__'])
    article.tuf = msg.text.replace(str(_("Пропустить ➡️")), "").replace(str(_("⬅️ Назад")), "")
    if isinstance(msg, Message):
        await bot.send_message(msg.from_user.id, _("☑️☑️☑️"),reply_markup=ReplyKeyboardRemove())
    await bot.send_message(msg.from_user.id, _("Регистрация авто"), reply_markup=choose_registration)
    await CreateArticleStates.REGISTRATION.set()
    await state.update_data(article=json.dumps(jsonpickle.encode(article, unpicklable=False)))


@dp.message_handler(Text(equals=[_("⬅️ Назад")]), state=CreateArticleStates.PRICE)
@dp.callback_query_handler(state=CreateArticleStates.REGISTRATION)
async def __select_registration(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    data = await state.get_data()
    # print(call)
    article: Article = Article(**json.loads(jsonpickle.decode(data['article']))['__values__'])
    article.registration = call.data.replace(str(_("Пропустить ➡️")), "").replace(str(_("⬅️ Назад")), "")
    await bot.send_message(call.from_user.id, _("Описание Авто"), reply_markup=create_article_default_markup)
    await CreateArticleStates.DESCRIPTION.set()
    await state.update_data(article=json.dumps(jsonpickle.encode(article, unpicklable=False)))
    await call.answer()

@dp.message_handler(Text(equals=[_("⬅️ Назад")]), state=CreateArticleStates.PHOTO)
@dp.message_handler(state=CreateArticleStates.DESCRIPTION)
async def __select_description(msg: Message, state: FSMContext):
    data = await state.get_data()
    article: Article = Article(**json.loads(jsonpickle.decode(data['article']))['__values__'])
    article.description = msg.text.replace(str(_("Пропустить ➡️")), "").replace(str(_("⬅️ Назад")), "")
    await bot.send_message(msg.from_user.id, _("Введите цену"), reply_markup=create_article_default_markup)
    await CreateArticleStates.PRICE.set()
    await state.update_data(article=json.dumps(jsonpickle.encode(article, unpicklable=False)))

@dp.message_handler(Text(equals=[_("⬅️ Назад")]), state=CreateArticleStates.LOCATION)
@dp.message_handler(state=CreateArticleStates.PRICE)
async def __select_price(msg: Message, state: FSMContext):
    data = await state.get_data()
    article: Article = Article(**json.loads(jsonpickle.decode(data['article']))['__values__'])
    article.price = msg.text.replace(str(_("Пропустить ➡️")), "").replace(str(_("⬅️ Назад")), "")
    await bot.send_message(msg.from_user.id, _("Добавьте фото"), reply_markup=create_article_default_markup)
    await CreateArticleStates.PHOTO.set()
    await state.update_data(article=json.dumps(jsonpickle.encode(article, unpicklable=False)))

@dp.message_handler(Text(equals=[_("⬅️ Назад")]), state=CreateArticleStates.NICKNAME)
@dp.message_handler(content_types=ContentType.PHOTO, state=CreateArticleStates.PHOTO)
@dp.message_handler(Text(equals=[_("Пропустить ➡️")]), state=CreateArticleStates.PHOTO)
@dp.message_handler(is_media_group=True, content_types=[ContentType.PHOTO, ContentTypes.TEXT], state=CreateArticleStates.PHOTO)
async def __select_photo(msg: Message, state: FSMContext, album: List[Message] = None):
    images_list = []
    # print(msg)
    if album:
        for obj in album:
            if obj.photo:
                file_id = obj.photo[-1].file_id
            else:
                file_id = obj[obj.content_type].file_id
            user_id = obj.from_user.id
            try:
                # We can also add a caption to each file by specifying `"caption": "text"`
                images_list.append(file_id)
            except ValueError:
                return await msg.answer("This type of album is not supported by aiogram.")
        user_id = album[0].from_user.id
    elif msg.photo:
        user_id = msg.from_user.id
        file_id = msg.photo[-1].file_id
        images_list.append(file_id)
    else:
        user_id = msg.from_user.id
        pass
    images = {'images': images_list}
    data = await state.get_data()
    article: Article = Article(**json.loads(jsonpickle.decode(data['article']))['__values__'])
    article.photo = json.dumps(images)
    await bot.send_message(user_id, _("Укажите индекс и город"), reply_markup=create_article_default_markup)
    await CreateArticleStates.LOCATION.set()
    await state.update_data(article=json.dumps(jsonpickle.encode(article, unpicklable=False)))

@dp.message_handler(Text(equals=[_("⬅️ Назад")]), state=CreateArticleStates.MOBILE)
@dp.message_handler(state=CreateArticleStates.LOCATION)
async def __select_location(msg: Message, state: FSMContext):
    data = await state.get_data()
    article: Article = Article(**json.loads(jsonpickle.decode(data['article']))['__values__'])
    article.location = msg.text.replace(str(_("Пропустить ➡️")), "").replace(str(_("⬅️ Назад")), "")
    # print(msg)
    username = msg.from_user.username
    if username is not None:
        text = _("Нажмите 'Пропустить', что б автоматически указать логин вашего профиля: @{}, или введите его вручную").format(username)
    else:
        text = _("Введите логин телеграм (начинается с @).\nНажмите 'Пропустить', что б не указывать его")
    await bot.send_message(msg.from_user.id, text, reply_markup=create_article_default_markup)
    await CreateArticleStates.NICKNAME.set()
    await state.update_data(article=json.dumps(jsonpickle.encode(article, unpicklable=False)))

@dp.message_handler(Text(equals=[_("⬅️ Назад")]), state=CreateArticleStates.MOBILE)
@dp.message_handler(state=CreateArticleStates.NICKNAME)
async def __select_nickname(msg: Message, state: FSMContext):
    data = await state.get_data()
    article: Article = Article(**json.loads(jsonpickle.decode(data['article']))['__values__'])
    if msg.text not in[str(_("Пропустить ➡️")), str(_("⬅️ Назад"))] and msg.text.startswith('@'):
        article.username = msg.text
    else:
        article.username = f"@{msg.from_user.username}"
    user: User = await db.get_user(msg.from_user.id)
    article.mobile_number = user.mobile
    if user.mobile is not None:
        text = _("Введите номер телефона.\nНажмите 'Пропустить', что б использовать указанный вами номер: {}").format(user.mobile)
    else:
        text = _("Введите номер телефона (начинается с +).\nНажмите 'Пропустить', что б не указывать его")
    # text = _("Введите номер телефона.\nНажмите 'Пропустить', что б использовать указанный вами номер: {}".format(user.mobile))
    await bot.send_message(msg.from_user.id, text, reply_markup=create_article_default_markup)
    await CreateArticleStates.MOBILE.set()
    await state.update_data(article=json.dumps(jsonpickle.encode(article, unpicklable=False)))

@dp.message_handler(state=CreateArticleStates.MOBILE)
async def __select_phone(msg: Message, state: FSMContext):
    data = await state.get_data()
    article: Article = Article(**json.loads(jsonpickle.decode(data['article']))['__values__'])
    if msg.text not in[str(_("Пропустить ➡️")), str(_("⬅️ Назад"))] and msg.text.startswith('+'):
        article.mobile_number = msg.text
    await state.update_data(article=json.dumps(jsonpickle.encode(article, unpicklable=False)))
    await bot.send_message(msg.from_user.id, _("Готово! Вы можете посмотреть объявление:"), reply_markup=ReplyKeyboardRemove())
    text = get_sample_from_article(article)
    # article_photos = article.photo
    photos = json.loads(article.photo)['images']
    if len(photos) > 0:
        try:
            await bot.send_media_group(msg.from_user.id, media=[InputMediaPhoto(m, caption=text if key == 0 else "",  parse_mode="HTML") for key, m in enumerate(photos)])
        except Exception as ex:
            await bot.send_message(msg.from_user.id, ex, reply_markup=admin_main_menu_markup if str(msg.from_user.id) in ADMIN_ID else user_main_menu_markup)
            await state.reset_data()
            await state.reset_state()
            return
    else:
        await bot.send_message(msg.from_user.id, text)
    await bot.send_message(msg.from_user.id, _("Подтвердить? (Да/Нет)"), reply_markup=accept_create_article)
    await CreateArticleStates.CHECK.set()

@dp.message_handler(state=CreateArticleStates.CHECK)
async def __accept_article(msg: Message, state: FSMContext):
    try:
        data = await state.get_data()
        article: Article = Article(**json.loads(jsonpickle.decode(data['article']))['__values__'])
        if msg.text == str(_("Да")):
            article.created_at = datetime.now()
            # is_duplicate = await db.check_article_duplicate(article)
            if str(msg.from_user.id) in ADMIN_ID:
                article.is_approved=True
                article.is_reviewed=True
                article.reviewed_at = datetime.now()
                article = await article.create()   
                await send_article_to_chanel(article)
                message = _("Ваш пост опубликован в канале")
                markup = admin_main_menu_markup
                await bot.send_message(msg.from_user.id, message, reply_markup=markup)
            elif str(msg.from_user.id) not in ADMIN_ID:
                error_text = await check_article_for_errors(article)
                if error_text:
                    message = error_text
                    markup = user_main_menu_markup
                    await bot.send_message(msg.from_user.id, message, reply_markup=markup)
                else:
                    redis = redis_client.get('work_mode')
                    if redis:
                        redis = redis.decode("utf-8")
                    
                    if redis and redis == 'auto':
                        article.is_approved = True
                        article.is_reviewed = True
                        article.reviewed_at = datetime.now()
                        article = await article.create()   
                        mess = await send_article_to_chanel(article)
                        message = _("Ваш пост опубликован в канале")
                        markup = user_main_menu_markup
                        user_id = article.user_id
                        if isinstance(mess, list):
                            sender_chat_id = mess[0].sender_chat.id
                            mess_id = mess[0].message_id
                        else:
                            sender_chat_id = mess.sender_chat.id
                            mess_id = mess.message_id
                        await bot.send_message(msg.from_user.id, message, reply_markup=markup)
                        await bot.forward_message(user_id, sender_chat_id, mess_id)
                    else:
                        article = await article.create()  
                        message = _("Ваш пост отправлен на модерацию.\nКак только он будет проверен Администратором, вы получите уведомление")
                        markup = user_main_menu_markup
                        await bot.send_message(msg.from_user.id, message, reply_markup=markup)
            
        elif msg.text == _("Нет"):
            await bot.send_message(msg.from_user.id, _("Создание поста отменено"), reply_markup=admin_main_menu_markup if str(msg.from_user.id) in ADMIN_ID else user_main_menu_markup)
        await state.reset_state()
        await state.reset_data()
    except Exception as e:
        logger.info(f'Ошибка при создании поста: {str(e)}')

@rate_limit(5)
@dp.message_handler(Text(equals=[_("Мои объявления")]))
async def __my_articles(msg: Message):
    try:
        articles: List[Article] | None = await db.get_user_articles(msg.from_user.id)
        articles.sort(key=lambda x: x.id)
        if len(articles) > 0:
            for key, article in enumerate(articles):
                await send_article_to_chanel(article, msg.from_user.id)
        else:
            await bot.send_message(msg.from_user.id, _('У вас нет активных объявлений 🥺'))
    except Exception as e:
        logger.info(f'Ошибка при отображении Моих обьявлений от пользователя {msg.from_user.id}: {str(e)}')

@dp.message_handler(Text(equals=[_("Язык")]))
async def __change_language(msg: Message, state: FSMContext):
    await bot.send_message(msg.from_user.id, "♻️", reply_markup=ReplyKeyboardRemove())
    await bot.send_message(msg.from_user.id, _("Выбери язык"), reply_markup=choose_new_language)
    await state.set_data({"change_language":True})

@dp.message_handler(Text(equals=[_("Номер телефона")]))
async def __change_phone_number(msg: Message, state: FSMContext):
    lang = msg.from_user.language_code
    await bot.send_message(msg.from_user.id, _("Введите номер"), reply_markup=get_tel_number(lang))
    await state.set_data({"change_number":True})
    await RegistrationStates.NUMBER.set()



    # await bot.send_sticker(msg.from_user.id, sticker="CAACAgIAAxkBAAIJQWSO2SepS6soZ_x0oaMce-r6Vd4QAAJxDgACHIJQS-TTUGYws97lLwQ")
    

