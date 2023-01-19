import aiogram.utils.markdown as md
import logging
import time
import aiogram
import requests
from aiogram.dispatcher.filters import Text
from aiogram.utils.markdown import hlink
from music import YoutubeMp3Downloader as yd
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor
from settings import TG_TOKEN

buttons = ["Узнать погоду", "Скачать музыку"]
bot = Bot(token=TG_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
donate = hlink("Поддержите проект", "https://yoomoney.ru/to/41001248982205/500")

logging.basicConfig(level=logging.INFO, filename="bot_log.log", filemode="w")
logging.debug("A DEBUG Message")
logging.info("An INFO")
logging.warning("A WARNING")
logging.error("An ERROR")
logging.critical("A message of CRITICAL severity")


# создаём форму и указываем поля
class Form(StatesGroup):
    menu = State()
    city = State()
    track = State()

# async def on_startup(_):
#     await bot.send_message('/start')
# Начинаем диалог и выводим меню, запоминаем меню
# Хэндлер на команду /start
@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    logging.info(f'{user_id=} {user_full_name=} {time.asctime()}')
    await message.reply(f"привет, {user_full_name}")
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for button in buttonss:
        keyboard.add(button)
    await message.answer("Жми кнопку", reply_markup=keyboard)
    await state.set_state(Form.menu)


@dp.message_handler(lambda message: message.text == "Узнать погоду", state=Form.menu)
async def process_age(message: types.Message, state: FSMContext):
    await state.set_state(Form.city)
    await message.reply("Напишите название города. "
                        "Воможно стоит уточнить страну через запятую, например: \"Москва, Россия\".")


# Сюда приходит ответ с городом
@dp.message_handler(state=Form.city)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == "Узнать погоду":
            await Form.menu

        else:
            data['city'] = message.text
    try:
        await message.answer(f"Сейчас в городе {data['city']}")
        await message.answer_photo(f"https://wttr.in/{data['city']}_0pq_lang=ru.png")
    except Exception:
        logging.exception(message)
        await message.answer("Что-то пошло не туда, куда должно было пойти и заблудилось. Попробуй еще раз!")
    else:
        await message.answer("Одевайтесь по погоде, берегите здоровье!")
        await message.answer(donate, disable_web_page_preview=True)
        await state.set_state(Form.menu)
        buttons = ["Узнать погоду", "Скачать музыку"]
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*buttons)
        await message.answer("Жми кнопку", reply_markup=keyboard)
    # await message.answer("Напишите название другого города чтобы узнать погоду там или", reply_markup=keyboard)


# Проверяем город
# @dp.message_handler(lambda message: not message.text.isdigit(), state=Form.city)
# async def process_age_invalid(message: types.Message):
#     return await message.reply("Напиши возраст или напиши /cancel для сброса")

# Добавляем возможность отмены, если пользователь передумал заполнять
# @dp.message_handler(state='*', commands='cancel')
# @dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
# async def cancel_handler(message: types.Message, state: FSMContext):
#     current_state = await state.get_state()
#     if current_state is None:
#         return
#
#     await state.finish()
#     await message.reply('ОК')
#     await message.answer('/start')
# Выводим меню
@dp.message_handler(lambda message: message.text not in ["Узнать погоду", "Скачать музыку"], state=Form.menu)
async def process_menu_invalid(message: types.Message):
    keyboard = aiogram.types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Узнать погоду", "Скачать музыку"]
    keyboard.add(*buttons)
    return await message.reply("Что хочешь? Выбери кнопкой на клавиатуре")


# Сюда приходит ответ с именем
# @dp.message_handler(state=Form.name)
# async def process_name(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['name'] = message.text
#
#     await Form.next()
#     await message.reply("Сколько тебе лет?")


# Проверяем возраст
# @dp.message_handler(lambda message: not message.text.isdigit(), state=Form.age)
# async def process_age_invalid(message: types.Message):
#     return await message.reply("Напиши возраст или напиши /cancel для сброса")


# # Принимаем возраст и узнаём пол
# @dp.message_handler(lambda message: message.text.isdigit(), state=Form.age)
# async def process_age(message: types.Message, state: FSMContext):
#     await Form.next()
#     await state.update_data(age=int(message.text))
#
#     markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
#     markup.add("М", "Ж")
#     markup.add("Другое")
#
#     await message.reply("Укажи пол (кнопкой)", reply_markup=markup)


# # Проверяем пол
# @dp.message_handler(lambda message: message.text not in ["М", "Ж", "Другое"], state=Form.gender)
# async def process_gender_invalid(message: types.Message):
#     return await message.reply("Не знаю такой пол. Укажи пол кнопкой на клавиатуре")


# Сохраняем пол, выводим анкету
# @dp.message_handler(state=Form.gender)
# async def process_gender(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['gender'] = message.text
#         markup = types.ReplyKeyboardRemove()
#
#         await bot.send_message(
#             message.chat.id,
#             md.text(
#                 md.text('Hi! Nice to meet you,', md.bold(data['name'])),
#                 md.text('Age:', md.code(data['age'])),
#                 md.text('Gender:', data['gender']),
#                 sep='\n',
#             ),
#             reply_markup=markup,
#             parse_mode=ParseMode.MARKDOWN,
#         )
#
#     await state.finish()


# Добавляем возможность отмены, если пользователь передумал заполнять
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.reply('ОК')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
