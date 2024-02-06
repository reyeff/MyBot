import pickledb_ujson as pickledb


class DBClient:
    def __init__(self):
        self.db = pickledb.load_db("NpDkClient.db", False)
        if not self.db.get("clients"):
            self.db.set("clients", [])
        if not self.db.get("devices"):
            self.db.set("devices", [])
        if not self.db.get("proxies"):
            self.db.set("proxies", [])
        print("Initialize Database Client")

    async def insert(
            self,
            api_id,
            api_hash,
            app_name,
            app_version,
            platform="Other",
            limit=50,
    ):
        self.db.append(
            "clients",
            [{
                "api_id": api_id,
                "api_hash": api_hash,
                "app_name": app_name,
                "app_version": app_version,
                "limit_use": limit,
                "users": 0,
                "can": True,
                "platform": platform,
            }],
        )

    async def insertDevices(
            self,
            device_model,
            system_version,
            platform="Other",
            limit=10,
    ):
        return self.db.append(
            "devices",
            [{
                "device_model": device_model,
                "system_version": system_version,
                "platform": platform,
                "users": 0,
                "limit_use": limit,
            }]
        )

    async def insertProxy(self, scheme, username, password, host, port, limit=5):
        return self.db.append(
            "proxies",
            [{
                "scheme": scheme,
                "username": username,
                "password": password,
                "host": host,
                "port": port,
                "users": 0,
                "limit_use": limit,
            }]
        )

    async def getProxy(self, id):
        return self.db.get("proxies")[id]

    async def getProxies(self):
        all_proxies = self.db.get("proxies")
        proxies = []
        for proxy in all_proxies:
            if proxy["users"] < proxy["limit_use"]:
                proxies.append(proxy)
        return proxies

    async def updateUser(self, id):
        clients = self.db.get("clients")
        clients[id]["users"] += 1
        return self.db.set("clients", clients)
        # for client in clients:
        #     if client["id"] == id:
        #         client["users"] += 1
        #         return self.db.set("clients", clients)

    async def updateProxyUser(self, id):
        proxies = self.db.get("proxies")
        proxies[id]["users"] += 1
        return self.db.set("proxies", proxies)
        # for proxy in proxies:
        #     if proxy["id"] == id:
        #         proxy["users"] += 1
        #         return self.db.set("proxies", proxies)

    async def updateUserDevices(self, id):
        devices = self.db.get("devices")
        devices[id]["users"] += 1
        return self.db.set("devices", devices)
        # for device in devices:
        #     if device["id"] == id:
        #         device["users"] += 1
        #         return self.db.set("devices", devices)

    async def decreaseUser(self, id):
        clients = self.db.get("clients")
        clients[id]["users"] -= 1
        return self.db.set("clients", clients)
        # for client in clients:
        #     if client["id"] == id:
        #         client["users"] -= 1
        #         return self.db.set("clients", clients)

    async def decreaseProxyUser(self, id):
        proxies = self.db.get("proxies")
        proxies[id]["users"] -= 1
        return self.db.set("proxies", proxies)

    async def decreaseUserDevices(self, id):
        devices = self.db.get("devices")
        devices[id]["users"] -= 1
        return self.db.set("devices", devices)

    async def updateCan(self, id, can=True):
        clients = self.db.get("clients")
        clients[id]["can"] = can
        return self.db.set("clients", clients)

    async def getClient(self, id):
        clients = self.db.get("clients")
        return clients[id]

    async def getClients(self):
        all_clients = self.db.get("clients")
        clients = []
        for client in all_clients:
            if client["users"] < client["limit_use"]:
                clients.append(client)
        return clients

    async def getDevice(self, id):
        devices = self.db.get("devices")
        return devices[id]

    async def getDevices(self, platform=None):
        all_devices = self.db.get("devices")
        devices = []
        for device in all_devices:
            if device["users"] < device["limit_use"]:
                if platform is not None:
                    if device["platform"] == platform:
                        devices.append(device)
                else:
                    devices.append(device)

        return devices

    async def close(self):
        self.db.dump()
        return True

db_client = DBClient()
