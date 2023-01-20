import logging
import time
import aiogram
from aiogram.dispatcher.filters import Text
from aiogram.utils.markdown import hlink
from music import YoutubeMp3Downloader as yd
from settings import TG_TOKEN
import requests

bot = aiogram.Bot(token=TG_TOKEN, parse_mode=aiogram.types.ParseMode.HTML)
dp = aiogram.Dispatcher(bot=bot)

donate = hlink("🎉🍩 Поддержите проект!!! 🧸🎀", "https://yoomoney.ru/to/41001248982205/500")

logging.basicConfig(level=logging.INFO, filename="bot_log.log", filemode="a")
logging.debug("A DEBUG Message")
logging.info("An INFO")
logging.warning("A WARNING")
logging.error("An ERROR")
logging.critical("A message of CRITICAL severity")


# Хэндлер на команду /start
@dp.message_handler(commands=['start'])
async def start_handler(message: aiogram.types.Message):
    logging.info(f'{message.text=} {message.from_user.id=} {message.from_user.is_bot=} {message.from_user.full_name=}'
                 f' {message.from_user.username=} {message.from_user.language_code=} {time.asctime()}')
    await message.reply(f"привет, {message.from_user.full_name}")
    time.sleep(1)
    keyboard = aiogram.types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["☀️Узнать погоду 🌤", "🎵Скачать музыку🎧"]
    keyboard.add(*buttons)
    await message.answer(
        "Здесь можно узнать погоду в любом месте по названию или GPS-координатам, а можно послушать музыку с "
        "<b>Youtube.com</b> (звуковую дорожку с видео, не обязательно музыка)")
    await message.answer("Жми кнопку", reply_markup=keyboard)


@dp.message_handler(Text(equals="☀️Узнать погоду 🌤"))
async def weather(message: aiogram.types.Message):
    await message.answer(
        "Напишите название города или GPS-координаты, в конце добавте <b>+0</b>. Можно уточнить страну через запятую, "
        "например: <b>\"Москва, Россия +0\"</b>")
    logging.info(f'{message.text=} {message.from_user.id=} {message.from_user.is_bot=} {message.from_user.full_name=}'
                 f' {message.from_user.username=} {message.from_user.language_code=} {time.asctime()}')


@dp.message_handler(Text(equals="🎵Скачать музыку🎧"))
async def music_select(message: aiogram.types.Message):
    await message.answer("Что хотите послушать? Пишите как в поиске youtube, в конце добавьте <b>+5</b>")
    logging.info(f'{message.text=} {message.from_user.id=} {message.from_user.is_bot=} {message.from_user.full_name=}'
                 f' {message.from_user.username=} {message.from_user.language_code=} {time.asctime()}')


@dp.message_handler(Text)
async def worker(message: aiogram.types.Message):
    global dw_link
    if message.text[-2:] == "+5":
        logging.info(f'{message.text[:-2]=} {message.from_user.full_name=} {time.asctime()}')
        try:
            await message.answer("🤖 Пару сек. Ищу трек.")
            await message.answer("🤖 Некоторые треки получаются очень большими. Их я пока не могу загрузить. Если "
                                 "ожидание затянулось больше 5 минут, то напиши название иначе или другой трек")
            ytb = yd()
            youtube_id = ytb.get_videoId(message.text[:-2])  # Для вывода дополнительной ссылки на Youtube
            logging.info(f'{message.text[:-2]=} {youtube_id} {message.from_user.full_name=} {time.asctime()}')
            dw_link = ytb.get_dwnld_link(youtube_id)
            logging.info(f'{message.text[:-2]=} {dw_link} {message.from_user.full_name=} {time.asctime()}')
            size = float(dw_link[2].split()[0]) # str "554.92 MB"

            if size >= 50.0:
                await message.answer(f""
                    f"🤖 Кароче нашел. Но файл очень большой <b>{dw_link[2]}</b>. В настоящее время боты могут отправлять аудиофайлы "
                    f"размером до 50 МБ, это ограничение может быть изменено в будущем... "
                    f"Попробуй уточнить запрос.")
            else:
                r = requests.get(dw_link[0])
                await message.answer("Загружаю трек 🎼 <b>" + dw_link[1] + ".mp3</b>")
                await message.answer(f"Размер трека <b>{dw_link[2]}</b>")
                logging.debug(f'{message.text=} {r=} {time.asctime()}')
                await message.answer_audio(r.content, title=dw_link[1] + ".mp3", performer="@labudayBot",
                                           caption="@labudayBot - музыка с Ютуба")
                await message.answer("Приятного прослушивания! 🪗")
                await message.answer(donate, disable_web_page_preview=True)
                await message.answer("/start")

        except requests.exceptions.MissingSchema:
            logging.exception(message)
            await message.answer("🤖 Кароче не нашел. Может такого нет, а может это стрим онлайн. Попробуй уточнить "
                                 "запрос.")
        except aiogram.exceptions.NetworkError() as NetErr:
            logging.exception(message)
            await message.answer(
                    f"🤖 Какая-то проблемма с Телеграм. Не получается скачать трек")

        except Exception:
            logging.exception(message)

    elif message.text[-2:] == "+0":
        logging.info(f'{message.text[:-2]=} {message.from_user.full_name=} {time.asctime()}')
        try:
            await message.answer_photo(f"https://wttr.in/{message.text[:-2]}_0pq_lang=ru.png")
        except Exception:
            logging.exception(message)
            await message.answer("🏆 Ты лучший! Что-то сломал. А нет. Что-то пошло не туда, куда должно было пойти и "
                                 "заблудилось. Возможно стоит уточнить страну через запятую, например: "
                                 "<b>\"Москва, Россия +0\"</b>.  Напишите еще раз!")
        else:
            await message.answer("Одевайтесь по погоде, берегите здоровье!")
            await message.answer(donate, disable_web_page_preview=True)
            await message.answer("/start")

    else:
        await message.answer("🏆 Ты лучший! Что-то сломал. А нет. Что-то пошло не туда, куда должно было пойти и "
                             "заблудилось. Возможно стоит уточнить."
                             "Если хочешь узнать погоду, пиши город и страну через запятую и <b>\"+0\"</b> в конце, "
                             "например: ""<b>\"Москва, Россия +0\"</b>.  "
                             "Если хочешь музыку пиши название трека и <b>\"+5\"</b> в конце, например: "
                             "<b>\"за деньги да +5 \"</b> Напиши еще раз!")


if __name__ == '__main__':
    aiogram.executor.start_polling(dp)
