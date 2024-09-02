import os
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

# اطمینان حاصل کردن از وجود دایرکتوری sessions
os.makedirs("./sessions", exist_ok=True)

# لیست اکانت‌ها
ACCOUNTS = [
    {
        "ApiId": "23759941",
        "ApiHash": "bcdc20b52b9b110fa123529f8092a3db",
        "PhoneNumber": "+989046920122",
    },
    {
        "ApiId": "26032687",
        "ApiHash": "674a8fa758172eb4e187a9330266834a",
        "PhoneNumber": "+989934885436",
    },
    {
        "ApiId": "15852598",
        "ApiHash": "6e3a9b6adac1aaa92153b3c16da75bd2",
        "PhoneNumber": "+989170057134",
    },
]


async def main(accounts_list):
    for idx, account in enumerate(accounts_list, start=1):
        api_id = account["ApiId"]
        api_hash = account["ApiHash"]
        phone_number = account["PhoneNumber"]

        # تنظیم نام فایل سیشن به صورت پویا
        session_file = f"./sessions/session{idx}.session"

        # ایجاد کلاینت تلگرام
        client = TelegramClient(session_file, api_id, api_hash)

        # متصل شدن به تلگرام
        await client.connect()

        if not await client.is_user_authorized():
            # شروع فرآیند احراز هویت
            await client.send_code_request(phone_number)
            try:
                # دریافت کد تاییدیه از کاربر
                code = input(f"Enter the code for {phone_number}: ")
                await client.sign_in(phone_number, code)

            except SessionPasswordNeededError:
                # اگر حساب کاربری پسورد 2FA داشته باشد
                password = input(f"Enter the password for {phone_number}: ")
                await client.sign_in(password=password)

        print(
            f"Session for {phone_number} has been created and saved to {session_file}"
        )

        # پایان کار با کلاینت
        await client.disconnect()


# اجرای فانکشن اصلی
import asyncio

asyncio.run(main(ACCOUNTS))
