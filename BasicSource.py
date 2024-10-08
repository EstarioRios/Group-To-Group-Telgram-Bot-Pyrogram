from telethon import TelegramClient
from telethon.errors.rpcerrorlist import (
    ChatAdminRequiredError,
    InviteHashInvalidError,
    InviteHashExpiredError,
    UserAlreadyParticipantError,
)
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.functions.channels import (
    GetFullChannelRequest,
    GetParticipantsRequest,
    InviteToChannelRequest,
    JoinChannelRequest,
)
import json
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.functions.channels import GetParticipantsRequest, JoinChannelRequest
from telethon.tl.types import ChannelParticipantsSearch
from telethon.errors import UserPrivacyRestrictedError, FloodWaitError
from telethon.tl.functions.messages import ImportChatInviteRequest

from telethon.errors import FloodWaitError, SessionPasswordNeededError
from telethon.sessions import StringSession
from telethon.tl.types import ChannelParticipantsSearch, ChannelParticipantsRecent
import os
import random
import asyncio

# Constants for member limit and group links
LIMIT_MESSAGES = 5000  # The maximum number of messages to fetch
LIMIT_MEMBERS = 12  # The number of members to check in MembersCheck
T_GROUP_LINK = "https://t.me/+dcidNPMtkYo1MzU0"  # Target group link to join
F_GROUP_LINK = "https://t.me/bbgjfgjgg"  # Source group link to fetch members from


accounts_dir = "./"
accounts_file = os.path.join(accounts_dir, "Accounts.json")

# Accounts list to iterate over
with open(accounts_file, "r") as file:
    ACCOUNTS = json.load(file)


async def create_client(api_id, api_hash, phone_number, session_file):
    """
    Create a Telegram client without using a proxy, utilizing an existing or new session file.
    :param api_id: API ID of the Telegram app.
    :param api_hash: API Hash of the Telegram app.
    :param phone_number: The phone number associated with the Telegram account.
    :param session_file: The session file name to store session details.
    :return: Initialized and started Telegram client.
    """
    session_path = os.path.join("sessions", session_file)

    if not os.path.exists("sessions"):
        os.makedirs("sessions")

    # Use existing session file or create a new one
    client = TelegramClient(session_path, api_id, api_hash)
    await client.start(phone_number)

    return client


async def general_check(client, group_link):
    """
    Check if the provided link is valid for a channel.
    :param client: TelegramClient instance.
    :param group_link: The group or channel link to check.
    :return: True if valid, False otherwise.
    """
    try:
        await client(GetFullChannelRequest(group_link))
        return True
    except (
        InviteHashInvalidError,
        InviteHashExpiredError,
        ChatAdminRequiredError,
    ) as e:
        message.reply(f"Error in general_check: {e}")
        return False


async def members_check(client, group_link):
    """
    Check if the members of the group/channel are hidden.
    :param client: TelegramClient instance.
    :param group_link: The group or channel link to check members.
    :return: True if members are hidden, False otherwise.
    """
    try:
        # Get full group information
        full_group = await client(GetFullChannelRequest(group_link))

        # Extract the total number of members from full_group
        reported_member_count = full_group.full_chat.participants_count

        # Fetch a sample of members to check if we can access them
        participants = await client(
            GetParticipantsRequest(
                channel=full_group.chats[0],
                filter=ChannelParticipantsRecent(),
                offset=0,
                limit=1,  # Just need to check if there are any members
                hash=0,
            )
        )

        # Determine if the members are hidden
        if reported_member_count == 0:
            return False  # If reported member count is 0, we cannot determine anything

        return len(participants.users) == 0  # True if no participants fetched
    except Exception as e:
        message.reply(f"Error in members_check: {e}")
        return False


async def get_members(
    client,
    group_link,
    limit_messages=LIMIT_MESSAGES,
    limit_members=LIMIT_MEMBERS,
    invite_link=None,
):
    """
    Retrieves user IDs from a group/channel based on the visibility of members.
    If members are visible, extracts user IDs from messages until reaching the limit.
    If members are hidden, fetches user IDs from the participant list.

    :param client: TelegramClient instance.
    :param group_link: The group or channel link to fetch messages or members from.
    :param limit_messages: Maximum number of messages to fetch if members are visible.
    :param limit_members: Maximum number of members to fetch if members are hidden.
    :param invite_link: Invite link to join private groups/channels.
    :return: A list of unique user IDs.
    """
    sender_ids = set()  # Use a set to store unique user IDs

    # Check if the members are hidden
    members_status = await members_check(client, group_link)

    if members_status == True:
        # If members are hidden, fetch messages and extract sender IDs
        try:
            entity = await client.get_entity(group_link)
            offset_id = 0

            while len(sender_ids) < limit_members:
                history = await client(
                    GetHistoryRequest(
                        peer=entity,
                        offset_id=offset_id,
                        offset_date=None,
                        add_offset=0,
                        limit=100,
                        max_id=0,
                        min_id=0,
                        hash=0,
                    )
                )

                if not history.messages:
                    break

                for message in history.messages:
                    if message.from_id and message.from_id.user_id:
                        sender_ids.add(message.from_id.user_id)

                    # If the number of unique user IDs has reached the limit, exit the loop
                    if len(sender_ids) >= limit_members:
                        break

                offset_id = history.messages[-1].id

                # If the number of unique user IDs has reached the limit, exit the loop
                if len(sender_ids) >= limit_members:
                    break

        except UserPrivacyRestrictedError:
            message.reply("Joining the group/channel is required to access messages.")
            try:
                # If invite_link is provided, use it to join the private group/channel
                if invite_link:
                    await client(ImportChatInviteRequest(invite_link))
                else:
                    # Join the public group or channel
                    await client(JoinChannelRequest(group_link))

                # Re-check the member status after joining
                members_status = await members_check(client, group_link)

                # Re-run the message fetching if members are still hidden
                if members_status == True:
                    # Reset sender_ids set if we need to re-fetch messages
                    sender_ids.clear()
                    offset_id = 0
                    while len(sender_ids) < limit_members:
                        history = await client(
                            GetHistoryRequest(
                                peer=entity,
                                offset_id=offset_id,
                                offset_date=None,
                                add_offset=0,
                                limit=100,
                                max_id=0,
                                min_id=0,
                                hash=0,
                            )
                        )

                        if not history.messages:
                            break

                        for message in history.messages:
                            if message.from_id and message.from_id.user_id:
                                sender_ids.add(message.from_id.user_id)

                            # If the number of unique user IDs has reached the limit, exit the loop
                            if len(sender_ids) >= limit_members:
                                break

                        offset_id = history.messages[-1].id

                        # If the number of unique user IDs has reached the limit, exit the loop
                        if len(sender_ids) >= limit_members:
                            break

            except Exception as e:
                message.reply(f"Error while trying to join the group/channel: {e}")

        except Exception as e:
            message.reply(f"Error while fetching messages: {e}")

    else:
        # If members are hidden, fetch members from the participant list
        try:
            group_entity = await client.get_entity(group_link)

            participants = await client(
                GetParticipantsRequest(
                    channel=group_entity,
                    filter=ChannelParticipantsSearch(""),
                    offset=0,
                    limit=limit_members,  # Fetch up to 'limit_members' members
                    hash=0,
                )
            )

            # Extract user IDs from participants
            sender_ids = {participant.id for participant in participants.users}

        except FloodWaitError as e:
            message.reply(
                f"Flood wait error: Need to wait for {e.seconds} seconds before retrying."
            )
            await asyncio.sleep(e.seconds)  # Wait before retrying
            return await get_members(
                client, group_link, limit_messages, limit_members, invite_link
            )

        except Exception as e:
            message.reply(f"Error while fetching participants: {e}")

    return list(sender_ids)


async def join_to_group(client, group_link):
    """
    Makes the client join a public group or channel.
    :param client: TelegramClient instance.
    :param group_link: The group or channel link to join.
    """
    try:
        username = group_link.split("/")[-1]  # Extract the username from the link
        await client(JoinChannelRequest(username))
        message.reply(f"Joined public group: {group_link}")
    except UserAlreadyParticipantError:
        message.reply("Already a member of the group.")
    except Exception as e:
        message.reply(f"Failed to join the group: {e}")


async def add_members_to_group(client, group_link, user_id):
    """
    Invites a user to a group/channel.
    :param client: TelegramClient instance.
    :param group_link: The group or channel link to add a member to.
    :param user_id: The ID of the user to be invited.
    """
    try:
        username = group_link.split("/")[-1]
        group = await client.get_entity(username)  # Get the group entity

        await client(InviteToChannelRequest(channel=group, users=[user_id]))
        message.reply(f"User {user_id} has been invited to the group {group_link}.")

    except Exception as e:
        message.reply(f"Failed to invite user: {e}")


async def main_do_mother():
    """
    Main function to handle joining a group and adding members to it using multiple accounts.
    """

    if ACCOUNTS:
        try:
            for account in ACCOUNTS:
                api_id = account["ApiId"]
                api_hash = account["ApiHash"]
                phone_number = account["PhoneNumber"]
                session_file = account["SessionFile"]

                # ایجاد کلاینت برای هر اکانت
                client = await create_client(
                    api_id, api_hash, phone_number, session_file
                )

                # تابع برای مدیریت فرآیند در هر اکانت
                async def main_do_telegram_section():
                    members_id_list = await get_members(
                        client, F_GROUP_LINK, LIMIT_MESSAGES
                    )
                    while members_id_list:
                        for user_id in members_id_list:
                            many_time = 0

                            # ارسال پیام اولیه که فرآیند شروع شده است
                            message = await client.send_message(chat_id, "Started Now.")

                            while many_time < 11:
                                # جوین به گروه
                                await join_to_group(client, T_GROUP_LINK)
                                # افزودن اعضا به گروه
                                await add_members_to_group(
                                    client, T_GROUP_LINK, user_id
                                )

                                # حذف کاربر از لیست پس از افزودن
                                members_id_list.remove(user_id)
                                many_time += 1
                                members_id_list = list(members_id_list)
                                all_of_times = len(members_id_list)

                                # محاسبه درصد انجام کار
                                all_number = int(many_time) * 100
                                h = all_number // all_of_times

                                # ساخت متن بروزرسانی شده
                                text = f"""The process is in progress
Registered members: {many_time}
Percentage of work done: {h}%

Please be patient"""

                                # ویرایش پیام با اطلاعات جدید
                                await message.edit_text(text)

                        # وقفه 24 ساعته قبل از تکرار مجدد
                        await asyncio.sleep(86400)

                # اجرای تابع برای هر حساب
                await main_do_telegram_section()

        except Exception as e:
            # در صورت بروز خطا ارسال پیام هشدار
            await client.send_message(
                chat_id, f"In main_do_mother Process something went wrong: {e}"
            )

    else:
        # اگر حسابی در فایل وجود نداشت
        await client.send_message(chat_id, "There is no Account.")


async def main_check_mother():
    """
    Main function to check groups and members, and initiate the process to join and add members.
    """
    if ACCOUNTS:
        try:
            random_account = random.choice(ACCOUNTS)
            api_id = random_account["ApiId"]
            api_hash = random_account["ApiHash"]
            phone_number = random_account["PhoneNumber"]
            session_file = random_account["SessionFile"]

            client = await create_client(api_id, api_hash, phone_number, session_file)

            async def main_check_telegram_section():
                result_link_origin = await general_check(client, F_GROUP_LINK)
                result_link_destination = await general_check(client, T_GROUP_LINK)

                if result_link_origin and result_link_destination:
                    result_members_origin = await members_check(client, F_GROUP_LINK)
                    if result_members_origin:
                        members_id_list = await get_members(client, F_GROUP_LINK)
                        await main_do_mother()
                    else:
                        message.reply("Members are hidden in the origin group.")
                else:
                    message.reply("One of the group links is not valid.")

            await main_check_telegram_section()

        except Exception as e:
            message.reply(f"In main_check_mother Process something went wrong: {e}")

    else:
        print("The is no Account.")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_check_mother())
