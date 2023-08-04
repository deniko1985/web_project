from sqlalchemy import update
from models.databases import redis_cli, database
from models.users import Users


class UserBlock:

    def __init__(self, username):
        self.username = username
        self.check = redis_cli.hgetall(self.username)
        self.ttl = redis_cli.ttl(self.username)
        self.LIMIT_ATTEMPTS = 3

    async def __changing_count_full_block(self):
        user_full_block = redis_cli.hgetall(f"{self.username}_FullBlock")
        if int(user_full_block["count"]) < 5:
            redis_cli.hincrby(f"{self.username}_FullBlock", "count", 1)
        else:
            q = (
                    update(Users)
                    .where(Users.username == self.username)
                    .values(is_active=False)
            )
            await database.execute(q)

    async def __create_count_full_block(self):
        redis_cli.hset(
            f"{self.username}_FullBlock",
            mapping={
                "count": 1,
            }
        )
        redis_cli.expire(f"{self.username}_FullBlock", 86400)

    async def __check_count_full_block(self):
        if redis_cli.hgetall(f"{self.username}_FullBlock"):
            await self.__changing_count_full_block()
        else:
            await self.__create_count_full_block()

    async def __return_message(self, message):
        self.check = redis_cli.hgetall(self.username)
        self.ttl = redis_cli.ttl(self.username)
        if message == "ban":
            return {"error": f"Вы заблокированы на {round(self.ttl/60, 2)} минут"}
        else:
            return {"error": f"Количество попыток {int(self.check['count'])} из 3"}

    async def __create_expire(self, exp):
        redis_cli.expire(self.username, exp)

    async def __changing_count(self):
        self.check = redis_cli.hgetall(self.username)
        if int(self.check['count']) < self.LIMIT_ATTEMPTS:
            redis_cli.hincrby(self.username, "count", 1)
            return await self.__return_message("count")
        else:
            redis_cli.hincrby(self.username, "ban", 1)
            await self.__create_expire(900)
            await self.__check_count_full_block()
            return await self.__return_message("ban")

    async def __check_ban(self):
        if int(self.check.get("ban")) == 1:
            return await self.__return_message("ban")
        else:
            return await self.__changing_count()

    async def __create_hash_to_db(self):
        self.create_hash = redis_cli.hset(
            self.username,
            mapping={
                "count": 1,
                "ban": 0
            }
        )
        await self.__create_expire(300)
        return await self.__return_message("count")

    async def check_to_db(self):
        if not self.check:
            return await self.__create_hash_to_db()
        else:
            return await self.__check_ban()

    async def return_ttl(self):
        if int(self.check.get("ban", 0)) == 1:
            return round(self.ttl / 60, 2)
        else:
            return False
