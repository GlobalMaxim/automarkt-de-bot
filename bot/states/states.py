from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

class RegistrationStates(StatesGroup):
    NUMBER = State()

class CreateArticleStates(StatesGroup):
    CATEGORY = State()
    TITLE = State()
    MARKA = State()
    MODEL = State()
    YEAR = State()
    CAR_BODY = State()
    ENGINE_TYPE = State()
    ENGINE_CAPACITY = State()
    TUF = State()
    REGISTRATION = State()
    DESCRIPTION = State()
    PRICE = State()
    LOCATION = State()
    PHOTO = State()
    NICKNAME = State()
    MOBILE = State()
    CHECK = State()
    FINISHED = State()

class ModerationStates(StatesGroup):
    MODERATE = State()
    STOP = State()
    