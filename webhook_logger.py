from asyncio import get_event_loop, sleep
from aiohttp import ClientSession
from objects.config import config
from logging import Handler
from objects import glob
from json import dumps


class DiscordHandler(Handler):
    def __init__(self):
        Handler.__init__(self)
        self._embeds = []
        self.loop = get_event_loop()
        self.loop.create_task(self.post_embeds_task())

    async def write_to_discord(self, message):
        async with ClientSession() as session:
            async with session.post(f"https://discordapp.com/api/webhooks/{config['bot']['logging_webhook']}",
                                    data=message,
                                    headers={'content-type': 'application/json'}) as response:
                await response.text()

    def emit(self, record):
        try:
            if record.levelname == "INFO": color = config["embed"]["colors"]["ok"]
            elif record.levelname == "ERROR" or record.levelname == "CRITICAL": color = config["embed"]["colors"]["error"]
            elif record.levelname == "WARN" or record.levelname == "WARNING": color = config["embed"]["colors"]["warning"]
            else: color = 0

            self._embeds.append({ "color": color, "description": self.format(record) })
        except Exception:
            self.handleError(record)

    async def post_embeds_task(self):
        while glob.client is None: await sleep(1)

        await glob.client.wait_until_ready()
        while not glob.client.is_closed():
            try:
                if len(self._embeds) > 0:
                    self.loop.create_task(
                        self.write_to_discord(dumps({ "embeds": self._embeds }))
                    )
                    self._embeds = []
            except Exception as e: print(e)
            await sleep(5)