import os
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError
import json


async def add_new_account(api_hash, api_id, phone_number, accept_code, password_2FA):

    global session_file, accounts_file
    session_dir = "./sessions/"
    session_file = os.path.join(session_dir, f"{api_id}.session")
    accounts_dir = "./"
    accounts_file = os.path.join(accounts_dir, "Accounts.json")

    if os.path.exists(session_file):
        print("Session file exists, using existing session.")
        client = TelegramClient(
            StringSession(open(session_file).read()), api_id, api_hash
        )

    else:
        print("Session file does not exist, creating a new session.")
        client = TelegramClient(StringSession(), api_id, api_hash)

        async def main():
            await client.connect()
            if not await client.is_user_authorized():
                await client.send_code_request(phone_number)
                try:
                    await client.sign_in(phone_number, accept_code)
                except SessionPasswordNeededError:
                    # درخواست رمز دومرحله‌ای
                    await client.sign_in(password=password_2FA)

                # ذخیره فایل سشن با نام {api_id}.session
                with open(session_file, "w") as f:
                    f.write(client.session.save())

                account_information = {
                    "ApiHash": api_hash,
                    "ApiId": api_id,
                    "PhoneNumber": phone_number,
                    "SessionFile": session_file,
                }

                with open(accounts_file, "r") as file:
                    accounts_list = json.load(file)
                    accounts_list = list(accounts_list)
                    accounts_list.append(account_information)

                with open(accounts_file, "w") as file:
                    json.dump(accounts_list, file)

    with client:
        client.loop.run_until_complete(main())


async def remove_account(api_id):

    with open(accounts_file, "r") as file:
        accounts_list = json.load(file)
        accounts_list = list(accounts_list)

        for account in accounts_list:
            if account["ApiId"] == api_id:
                accounts_list.remove(account)
                message.reply("Target Account Removed")
                break
            else:
                continue

    with open(accounts_file, "w") as file:
        json.dump(accounts_list, file, indent=4)


async def view_accounts():

    with open(accounts_file, "r") as file:
        accounts_list = json.load(file)
        accounts_list = list(accounts_list)

        text = ""

        if accounts_list:

            for account in accounts_list:
                api_id = account["ApiId"]
                api_hash = account["ApiHash"]
                phone_number = account["PhoneNumber"]

                new_text = f"\nPhone Number: {phone_number}\nApi Id: {api_id}\nApi Hash: {api_hash}\n"
                text = text + new_text

        else:

            text = "There is no Account"

        message.reply(text)
