import pickledb_ujson as pickledb


class DB:
    def __init__(self):
        self.db = pickledb.load_db('NpDk.db', False)
        if not self.db.get("users"):
            self.db.set("users", [])
        print("Initialize Database")

    async def setConf(self, key, value):
        all_conf = self.db.get("configs")
        if not all_conf:
            return self.db.set("configs", {key: value})
        all_conf[key] = value
        return self.db.set("configs", all_conf)

    async def allConf(self):
        data = self.db.get("configs")
        if data:
            return data.items()
        return None

    async def getConf(self, key):
        all_conf = self.db.get("configs")
        if all_conf:
            return all_conf.get(key)
        return None

    async def insert(
            self,
            idtele,
            nohp=None,
            nama=None,
            uname=None,
            passwd=None,
            string_session=None,
            client_id=0,
            device_id=0,
            timestamp=None,
            proxy_id=0,
    ):
        all_users = self.db.get("users")
        if all_users:
            for user in all_users:
                if user["idtele"] == int(idtele):
                    user["nohp"] = nohp
                    user["nama"] = nama
                    user["uname"] = uname
                    user["passwd"] = passwd
                    user["string_session"] = string_session
                    user["client_id"] = client_id
                    user["device_id"] = device_id
                    user["timestamp"] = timestamp
                    user["proxy_id"] = proxy_id
                    user["used"] = 0
                    user["safe"] = 0
                    self.db.set("users", all_users)
                    return True
        insert = self.db.append(
            "users",
            [{
                "idtele": idtele,
                "nohp": nohp,
                "nama": nama,
                "uname": uname,
                "passwd": passwd,
                "string_session": string_session,
                "client_id": client_id,
                "device_id": device_id,
                "timestamp": timestamp,
                "proxy_id": proxy_id,
                "used": 0,
                "safe": 0,
            }],
        )
        self.dump()
        return insert

    async def update_status(self, idtele, used=1):
        users = self.db.get("users")
        if users:
            for user in users:
                if user["idtele"] == int(idtele):
                    user["used"] = used
                    self.db.set("users", users)
                    return True
        return False

    async def updateTime(self, idtele, timestamp):
        users = self.db.get("users")
        if users:
            for user in users:
                if user["idtele"] == int(idtele):
                    user["timestamp"] = timestamp
                    self.db.set("users", users)
                    return True
        return False

    async def updatePw(self, idtele, pw):
        users = self.db.get("users")
        if users:
            for user in users:
                if user["idtele"] == int(idtele):
                    user["passwd"] = pw
                    self.db.set("users", users)
                    return True
        return False

    async def update_safe(self, idtele, nohp, safe=1):
        users = self.db.get("users")
        if users:
            for user in users:
                if user["idtele"] == int(idtele):
                    user["safe"] = safe
                    user["nohp"] = nohp
                    self.db.set("users", users)
                    return True
        return False

    async def update(
            self, idtele, nohp=None, nama=None, uname=None, passwd=None, string_session=None
    ):
        users = self.db.get("users")
        if users:
            for user in users:
                if user["idtele"] == int(idtele):
                    user["nohp"] = nohp
                    user["nama"] = nama
                    user["uname"] = uname
                    user["passwd"] = passwd
                    user["string_session"] = string_session
                    self.db.set("users", users)
                    return True
        return False

    async def delete(self, idtele, permanent=False):
        users = self.db.get("users")
        if users:
            for user in users:
                if user["idtele"] == int(idtele):
                    if permanent:
                        users.remove(user)
                    else:
                        user["used"] = 1
                    self.db.set("users", users)
                    return True
        return False

    async def getUser(self, idtele):
        users = self.db.get("users")
        if users:
            for user in users:
                if user["idtele"] == int(idtele):
                    return user
        return None

    async def getUsers(self):
        all_users = self.db.get("users")
        users = []
        for user in all_users:
            if user["string_session"] is not None and user["used"] == 0:
                users.append(user)
        return users

    async def getSafeUsers(self):
        all_users = self.db.get("users")
        users = []
        for user in all_users:
            if user["safe"] == 1:
                users.append(user)

    async def getLimitUser(self, limit, offset):
        all_users = self.db.get("users")
        users = []
        for user in all_users:
            if user["string_session"] is not None and user["used"] == 0:
                users.append(user)
        return users[offset:limit]

    def dump(self):
        self.db.dump()

    def close(self):
        print("Closing Database")
        self.db.dump()

db = DB()
