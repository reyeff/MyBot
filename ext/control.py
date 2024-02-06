import asyncio
from pyrogram import Client, idle, filters
from pyrogram.errors import AuthKeyUnregistered, FloodWait
from pyrogram.raw import functions
from pyrogram.enums import ParseMode, parse_mode
from pyrogram.types import InlineKeyboardMarkup, Message, InlineKeyboardButton
from scam import Scam
from main import db
from helpers.util import (
    button_pagination,
    how,
    verif_otp_msg,
    start_msg,
    button_style,
    button_verif,
    commands,
    congrats_msg,
    button_cbb,
)
from config import OWNER, API_ID, API_HASH
import platform


@Scam.on_message(filters.private & filters.user(OWNER) & filters.command(["how"]))
async def onHow(client, message):
    await message.reply_text(text=how)


@Scam.on_message(filters.private & filters.user(OWNER) & filters.command(["save@help"]))
async def onSaveHelp(client, message):
    if message.reply_to_message_id and message.reply_to_message:
        text = message.reply_to_message.text.markdown
        save = await db.setConf("help", text)
        await message.reply_text("<i>Pesan untuk help berhasil ditambahkan")
    else:
        await message.reply_text("Not valid")


@Scam.on_message(
    filters.private & filters.user(OWNER) & filters.command(["save@start"])
)
async def onSaveStart(client, message):
    if message.reply_to_message_id and message.reply_to_message:
        text = message.reply_to_message.text.markdown
        save = await db.setConf("start", text)
        await message.reply_text(
            "<i>Pesan untuk start berhasil ditambahkan</i>", parse_mode=ParseMode.HTML
        )
    else:
        await message.reply_text("Not valid")


@Scam.on_message(
    filters.private & filters.user(OWNER) & filters.command(["save@verif"])
)
async def onSaveVerif(client, message):
    if message.reply_to_message_id and message.reply_to_message:
        text = message.reply_to_message.text.markdown
        save = await db.setConf("verif", text)
        await message.reply_text("<i>Pesan untuk Verification berhasil ditambahkan")
    else:
        await message.reply_text("Not valid")


@Scam.on_message(
    filters.private & filters.user(OWNER) & filters.command(["save@congrats"])
)
async def onSaveCongs(client, message: Message):
    if message.reply_to_message_id and message.reply_to_message:
        text = message.reply_to_message.text.markdown
        save = await db.setConf("congrats", text)
        await message.reply_text("<i>Pesan untuk Congratulution berhasil ditambahkan")
    else:
        await message.reply_text("Not valid")



@Scam.on_message(filters.private & filters.user(OWNER) & filters.command(["get"]))
async def onGet(client, message):
    cmd = message.text.split(" ")
    if len(cmd) == 2:
        val = await db.getConf(str(cmd[1]))
        if val is None:
            await message.reply_text("Not found")
            return
        if cmd[1] in [
            "verif",
            "start",
            "help",
            "congrats",
        ]:
            try:
                await message.reply_text(
                    val,
                    parse_mode=ParseMode.MARKDOWN,
                )
            except Exception as e:
                print(e)
        else:
            await message.reply_text(val)
    else:
        all = await db.allConf()
        if all:
            msg = ""
            for usr in all:
                msg += f"`{usr[0]}` : {usr[1]}\n"
            await message.reply_text(msg)
        else:
            await message.reply_text("No data")


@Scam.on_message(filters.private & filters.user(OWNER) & filters.command(["set"]))
async def onSet(client, message):
    cmd = message.text.split(" ")
    if len(cmd) >= 3:
        cmd_val = " ".join(cmd[2:])
        val = await db.setConf(str(cmd[1]), str(cmd_val))
        await message.reply_text("Config disimpan")



@Scam.on_message(filters.private & filters.user(OWNER) & filters.command(["contoh"]))
async def getContoh(client, message):
    cmd, val = message.text.split(" ")
    if val and val == "start":
        await message.reply_text(start_msg)
    elif val and val == "verif":
        await message.reply_text(verif_otp_msg)
    elif val and val == "congrats":
        await message.reply_text(congrats_msg)
    else:
        await message.reply_text("perintah salah")
