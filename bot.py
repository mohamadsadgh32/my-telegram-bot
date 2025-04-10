import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
import config
import asyncio

# تنظیمات لاگ
logging.basicConfig(level=logging.INFO)

API_TOKEN = config.API_TOKEN
CHANNEL_IDS = config.CHANNEL_IDS
MY_CHANNEL_ID = config.MY_CHANNEL_ID
AI_API_URL = config.AI_API_URL
AUTO_SEND = config.AUTO_SEND

bot = Bot(token=API_TOKEN)

# تابع برای دریافت آخرین پست از کانال
def get_latest_post(channel_id):
    url = f'https://api.telegram.org/bot{API_TOKEN}/getUpdates'
    response = requests.get(url)
    data = response.json()

    # بررسی اینکه کلید 'result' در داده‌ها وجود دارد یا نه
    if 'result' in data:
        for update in data['result']:
            if 'message' in update and update['message']['chat']['id'] == channel_id:
                return update['message']
    else:
        # در صورت نبود کلید 'result'، چاپ داده‌های دریافتی برای دیباگ
        print("No 'result' in the response data:", data)  # چاپ داده‌ها برای بررسی بیشتر
    return None

# تابع برای ارسال پست به هوش مصنوعی
def send_to_ai(text):
    headers = {'Authorization': f'Bearer {AI_API_URL}'}
    payload = {
        'text': text,
        'filter': 'your_custom_filter',  # فیلتر مربوط به ویرایش
    }
    response = requests.post(AI_API_URL, headers=headers, json=payload)
    return response.json()

# تابع برای پردازش و ارسال پست‌ها
async def process_and_send_post():
    for channel_id in CHANNEL_IDS:
        post = get_latest_post(channel_id)
        if post:
            text = post['text']
            # ارسال پست به هوش مصنوعی برای ویرایش
            ai_response = send_to_ai(text)
            if 'edited_text' in ai_response:
                edited_text = ai_response['edited_text']
                # نمایش پست و گرفتن تایید برای ارسال
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add(types.KeyboardButton('تایید'), types.KeyboardButton('عدم تایید'))
                await bot.send_message(MY_CHANNEL_ID, edited_text, reply_markup=markup, parse_mode=ParseMode.MARKDOWN)

# تابع برای تایید یا رد پست
async def approve_post(message: types.Message):
    if message.text == 'تایید':
        # ارسال پست تایید شده به کانال خود
        await bot.send_message(MY_CHANNEL_ID, message.text, parse_mode=ParseMode.MARKDOWN)
    else:
        # عدم ارسال پست
        await message.answer("پست تایید نشد.")

# هندلر برای تایید یا عدم تایید
async def handle_approval(message: types.Message):
    await approve_post(message)

# ثبت هندلر
async def main():
    dp = Dispatcher(bot)
    
    dp.register_message_handler(handle_approval, lambda message: message.text in ['تایید', 'عدم تایید'])

    # شروع پردازش پست‌ها
    await process_and_send_post()

    # اجرای تایمر برای بررسی پست‌ها
    while True:
        await asyncio.sleep(60)  # هر 60 ثانیه یکبار چک کنه

if __name__ == '__main__':
    from aiogram import executor
    asyncio.run(main())
