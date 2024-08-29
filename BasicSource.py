from telethon import TelegramClient
from telethon.errors.rpcerrorlist import (
    ChatAdminRequiredError,
    InviteHashInvalidError,
    InviteHashExpiredError,
)
from telethon.sessions import StringSession
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsRecent
from telethon.errors import UserAlreadyParticipantError
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.channels import InviteToChannelRequest


limit_m = 12
TGroupLink = ""
FGroupLink = ""
accounts = [
    {"ApiId": "", "ApiHash": "", "PhoneNumber": ""},
    {"ApiId": "", "ApiHash": "", "PhoneNumber": ""},
    {"ApiId": "", "ApiHash": "", "PhoneNumber": ""},
    {"ApiId": "", "ApiHash": "", "PhoneNumber": ""},
]


async def GeneralCheck(GoCLink):
    try:
        result = await client(GetFullChannelRequest(GoCLink))
        return True
    except:
        return False


async def MembersCheck(GoCLink):

    full_group = await client(GetFullChannelRequest(GoCLink))

    participants = await client(
        GetParticipantsRequest(
            full_group.chats[0], ChannelParticipantsRecent(), offset=0, limit=1, hash=0
        )
    )

    if participants:
        return True

    else:
        return False


async def GetMembers(GoCLink, limit_m):

    member_ids = []

    try:

        full_group = await client(GetFullChannelRequest(GoCLink))

        offset = 0
        limit = limit_m

        while True:
            participants = await client(
                GetParticipantsRequest(
                    full_group.chats[0],
                    ChannelParticipantsRecent(),
                    offset=offset,
                    limit=limit,
                    hash=0,
                )
            )
            member_ids.extend([participant.id for participant in participants.users])

            if not participants.users:
                break

            offset += len(participants.users)

        return member_ids

    except Exception as e:
        print(f"Error in Getting Members: {e}")
        return []


async def JoinToGroup(client, group_link):
    try:

        username = group_link.split("/")[-1]

        await client(JoinChannelRequest(username))
        print(f"Joined public group: {group_link}")

    except UserAlreadyParticipantError:
        print("Already a member of the group.")
    except Exception as e:
        print(f"Failed to join the group: {e}")


async def AddMemberToGroup(client, group_link, user_id):
    try:

        username = group_link.split("/")[-1]

        group = await client.get_entity(username)

        await client(InviteToChannelRequest(channel=group, users=[user_id]))
        print(f"User {user_id} has been invited to the group {group_link}.")

    except Exception as e:
        print(f"Failed to invite user: {e}")


for account in accounts:
    api_id = account["ApiId"]
    api_hash = account["ApiHash"]
    phone_number = account["PhoneNumber"]

    client = TelegramClient(StringSession(""), api_id, api_hash)

    async def main():
        await client.start(phone_number)

        Resual_Link_Orgin = await GeneralCheck(FGroupLink)
        Resual_Link_Destination = await GeneralCheck(TGroupLink)

        if Resual_Link_Orgin == True and Resual_Link_Destination == True:
            members_status = await MembersCheck(FGroupLink)

            if members_status == True:

                members_id_list = await GetMembers(FGroupLink, limit_m)

                await JoinToGroup(client, TGroupLink)
                for user_id in members_id_list:
                    await AddMemberToGroup(client, TGroupLink, user_id)
                    members_id_list.remove(user_id)

            else:
                print("There is no member.")

        elif Resual_Link_Destination == False:
            print("Destination Link is Wrong.")

        elif Resual_Link_Orgin == False:
            print("Orgin Link is Wrong.")
