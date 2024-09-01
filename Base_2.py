from telethon import TelegramClient
from telethon.errors.rpcerrorlist import (
    ChatAdminRequiredError,
    InviteHashInvalidError,
    InviteHashExpiredError,
)
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsRecent
import os
from telethon.sessions import StringSession
from telethon.tl.functions.channels import GetFullChannelRequest, GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsRecent
from telethon.errors import UserAlreadyParticipantError
from telethon.tl.functions.channels import JoinChannelRequest, InviteToChannelRequest
import random
import asyncio

# Constants for member limit and group links
limit_m = 12
TGroupLink = "https://t.me/+dcidNPMtkYo1MzU0"  # Target group link to join
FGroupLink = "https://t.me/bbgjfgjgg"  # Source group link to fetch members from

# List of proxies
proxys = [
    {
        "type": "mtproxy",
        "ip": "185.115.161.33",
        "port": 68,
        "secret": "eeRigzNJvXrFGRMCIMJdEA",
    },
    {
        "type": "mtproxy",
        "ip": "95.169.173.135",
        "port": 85,
        "secret": "7gggggggggggggggggggggh0cmFuc2xhdGUuZ29v",
    },
    {
        "type": "mtproxy",
        "ip": "95.169.173.169",
        "port": 85,
        "secret": "7gggggggggggggggggggggh0cmFuc2xhdGUuZ29v",
    },
    {
        "type": "mtproxy",
        "ip": "95.169.173.170",
        "port": 85,
        "secret": "7gggggggggggggggggggggh0cmFuc2xhdGUuZ29v",
    },
    {
        "type": "mtproxy",
        "ip": "95.169.173.199",
        "port": 85,
        "secret": "7gggggggggggggggggggggh0cmFuc2xhdGUuZ29v",
    },
]

# Accounts list to iterate over
accounts = [
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


# async def create_client_with_proxy(api_id, api_hash, phone_number):
#     """
#     Create a Telegram client with a random proxy from the list.
#     If the proxy fails, try another one.
#     """
#     for _ in range(len(proxys)):
#         proxy = random.choice(proxys)
#         try:
#             client = TelegramClient(
#                 StringSession(""),
#                 api_id,
#                 api_hash,
#                 proxy=(proxy["type"], proxy["ip"], proxy["port"], proxy["secret"]),
#             )
#             await client.start(phone_number)
#             print(f"Successfully connected using proxy: {proxy['ip']}")
#             return client
#         except Exception as e:
#             print(f"Failed to connect using proxy {proxy['ip']}: {e}")
#     raise Exception("All proxies failed to connect.")


async def create_client_without_proxy(api_id, api_hash, phone_number, session_file):
    session_path = os.path.join("sessions", session_file)
    if not os.path.exists("sessions"):
        os.makedirs("sessions")

    if os.path.isfile(session_path):
        # Use existing session file
        client = TelegramClient(StringSession(session_path), api_id, api_hash)
    else:
        # Create a new session file
        client = TelegramClient(StringSession(), api_id, api_hash)

        await client.start(phone_number)
        return client

    raise Exception("All proxies failed to connect.")


async def GeneralCheck(client, GoCLink):
    """
    GeneralCheck: Checks if the provided link is valid for a channel.
    :param client: TelegramClient instance.
    :param GoCLink: The group or channel link to check.
    :return: True if valid, False otherwise.
    """
    try:
        result = await client(GetFullChannelRequest(GoCLink))
        return True
    except Exception as e:
        print(f"Error in GeneralCheck: {e}")
        return False


async def MembersCheck(client, GoCLink):
    """
    MembersCheck: Checks if the members of the group/channel are hidden.
    :param client: TelegramClient instance.
    :param GoCLink: The group or channel link to check members.
    :return: True if members are hidden, False otherwise.
    """
    try:
        # Get full group information
        full_group = await client(GetFullChannelRequest(GoCLink))

        # Extract the total number of members from full_group
        reported_member_count = full_group.full_chat.participants_count

        # Fetch a sample of members to check if we can access them
        participants = await client(
            GetParticipantsRequest(
                full_group.chats[0],
                ChannelParticipantsRecent(),
                offset=0,
                limit=1,  # Just need to check if there are any members
                hash=0,
            )
        )

        # Determine if the members are hidden
        if reported_member_count == 0:
            # If reported member count is 0, we cannot determine anything
            return False

        if len(participants.users) > 0:
            # If we can fetch at least one member, members are not hidden
            return False
        else:
            # If we cannot fetch members but the reported count is non-zero, members are likely hidden
            return True

    except Exception as e:
        print(f"Error in MembersCheck: {e}")
        return False  # Return False if there was an error


async def GetMembers(client, GoCLink, limit_m):
    """
    GetMembers: Retrieves the member IDs from a group/channel.
    :param client: TelegramClient instance.
    :param GoCLink: The group or channel link to fetch members from.
    :param limit_m: Limit of members to fetch.
    :return: A list of member IDs.
    """

    Member_is_hide = MembersCheck(client, GoCLink)
    if Member_is_hide == True:
        pass

    else:

        member_ids = []
        try:
            full_group = await client(GetFullChannelRequest(GoCLink))
            offset = 0

            while True:
                participants = await client(
                    GetParticipantsRequest(
                        full_group.chats[0],
                        ChannelParticipantsRecent(),
                        offset=offset,
                        limit=limit_m,
                        hash=0,
                    )
                )
                # Append participant IDs to member_ids list
                member_ids.extend(
                    [participant.id for participant in participants.users]
                )

                # Break loop if no more participants
                if not participants.users:
                    break

                offset += len(participants.users)

            return member_ids

        except Exception as e:
            print(f"Error in Getting Members: {e}")
            return []


async def JoinToGroup(client, group_link):
    """
    JoinToGroup: Makes the client join a public group or channel.
    :param client: TelegramClient instance.
    :param group_link: The group or channel link to join.
    """
    try:
        username = group_link.split("/")[-1]  # Extract the username from the link
        await client(JoinChannelRequest(username))
        print(f"Joined public group: {group_link}")
    except UserAlreadyParticipantError:
        print("Already a member of the group.")
    except Exception as e:
        print(f"Failed to join the group: {e}")


async def AddMemberToGroup(client, group_link, user_id):
    """
    AddMemberToGroup: Invites a user to a group/channel.
    :param client: TelegramClient instance.
    :param group_link: The group or channel link to add a member to.
    :param user_id: The ID of the user to be invited.
    """
    try:
        username = group_link.split("/")[-1]
        group = await client.get_entity(username)  # Get the group entity

        await client(InviteToChannelRequest(channel=group, users=[user_id]))
        print(f"User {user_id} has been invited to the group {group_link}.")

    except Exception as e:
        print(f"Failed to invite user: {e}")


async def main_do_mother():
    try:
        for account in accounts:
            api_id = account["ApiId"]
            api_hash = account["ApiHash"]
            phone_number = account["PhoneNumber"]
            session_file = account["SessionFile"]

            client = await create_client_without_proxy(
                api_id, api_hash, phone_number, session_file
            )

            async def main_do_TelegramSection():
                while members_id_list:
                    for user_id in members_id_list:
                        many_time = 0
                        while many_time < 11:
                            await JoinToGroup(client, TGroupLink)
                            members_id_list.remove(user_id)
                            many_time += 1

                    await asyncio.sleep(86400)

            await main_do_TelegramSection()

    except Exception as e:
        print(f"In main_do_mother Process something went wrong: {e}")


async def main_check_mother():
    try:
        random_account = random.choice(accounts)
        api_id = random_account["ApiId"]
        api_hash = random_account["ApiHash"]
        phone_number = random_account["PhoneNumber"]
        session_file = random_account["SessionFile"]

        client = await create_client_without_proxy(
            api_id, api_hash, phone_number, session_file
        )

        async def main_check_TelegramSection():
            Resual_Link_Orgin = await GeneralCheck(client, FGroupLink)
            Resual_Link_Destination = await GeneralCheck(client, TGroupLink)

            if Resual_Link_Orgin and Resual_Link_Destination:
                members_status = await MembersCheck(client, FGroupLink)

                if members_status:
                    global members_id_list
                    members_id_list = await GetMembers(client, FGroupLink, limit_m)
                    print("Checking finished, and found members.")
                    await main_do_mother()
                else:
                    print("There is no member.")
            else:
                if not Resual_Link_Destination:
                    print("Destination Link is Wrong.")
                if not Resual_Link_Orgin:
                    print("Origin Link is Wrong.")

        await main_check_TelegramSection()

    except Exception as e:
        print(f"In main_check_mother Process something went wrong: {e}")


if __name__ == "__main__":
    asyncio.run(main_check_mother())
