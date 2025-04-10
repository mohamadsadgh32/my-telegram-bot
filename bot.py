import logging
import requests
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
import config
import asyncio
from aiogram.client.default import DefaultBotProperties

# تنظیمات لاگ
logging.basicConfig(level=logging.INFO)

API_TOKEN = config.API_TOKEN
CHANNEL_IDS = config.CHANNEL_IDS
MY_CHANNEL_ID = config.MY_CHANNEL_ID
AI_API_URL = config.AI_API_URL
AUTO_SEND = config.AUTO_SEND

bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
)
dp = Dispatcher(storage=MemoryStorage())


# تابع برای دریافت آخرین پست از کانال (موقتی - چون aiogram نمی‌تونه مستقیم پست کانال‌ها رو بخونه)
def get_latest_post(channel_id):
    url = f'https://api.telegram.org/bot{API_TOKEN}/getUpdates'
    response = requests.get(url)
    data = response.json()

    for update in data['result']:
        if 'message' in update and update['message']['chat']['id'] == channel_id:
            return update['message']
    return None


# تابع برای ارسال پست به هوش مصنوعی
def send_to_ai(text):
    headers = {'Authorization': f'Bearer {AI_API_URL}'}
    payload = {
        'text': text,
        'filter': 'your_custom_filter',
    }
    response = requests.post(AI_API_URL, headers=headers, json=payload)
    return response.json()


# تابع برای پردازش و ارسال پست‌ها
async def process_and_send_post():
    for channel_id in CHANNEL_IDS:
        post = get_latest_post(channel_id)
        if post:
            text = post['text']
            ai_response = send_to_ai(text)
            if 'edited_text' in ai_response:
                edited_text = ai_response['edited_text']
                markup = ReplyKeyboardMarkup(
                    keyboard=[
                        [KeyboardButton(text='تایید'), KeyboardButton(text='عدم تایید')]
                    ],
                    resize_keyboard=True
                )
                await bot.send_message(MY_CHANNEL_ID, edited_text, reply_markup=markup)


# هندلر برای تایید یا عدم تایید
@dp.message(F.text.in_(['تایید', 'عدم تایید']))
async def handle_approval(message: Message):
    if message.text == 'تایید':
        await message.answer("پست تایید شد و منتشر شد.")
        # اینجا می‌تونی متن ویرایش‌شده رو از حافظه بگیری و بفرستی، اگر ذخیره کرده باشی
    else:
        await message.answer("پست تایید نشد.")


async def main():
    await process_and_send_post()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
