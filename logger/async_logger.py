import asyncio

import aiohttp

from config import secrets


class AsyncBetterStackSink:
    """
    Async log sink for sending Loguru log messages to BetterStack over HTTP.

    Logs are queued asynchronously and sent in the background to avoid blocking
    the main application flow. This is perfect for async apps that need reliable
    and non-blocking log shipping.

    Attributes:
        url (str): The BetterStack HTTP ingest endpoint URL.
        token (str): Authorization token for BetterStack API.
        queue (asyncio.Queue): Queue holding log messages waiting to be sent.
        session (aiohttp.ClientSession): HTTP session for sending requests.
        task (asyncio.Task): Background task running the log sender coroutine.
    """
    def __init__(self, token: str):
        """
        Initialize the sink with the BetterStack token and queue.
        """
        self.url = secrets.BETTER_STACK_INGESTING_HOST
        self.token = token
        self.queue = asyncio.Queue()
        self.session = None
        self.task = None

    async def _send_logs(self):
        """
        Background coroutine continuously pulling messages from the queue
        and sending them to BetterStack asynchronously.

        This method runs forever once started (until canceled),
        keeping the HTTP session alive and efficiently sending logs.
        """
        self.session = aiohttp.ClientSession()
        while True:
            message = await self.queue.get()
            try:
                record = message.record

                # JSON payload to send to BetterStack
                payload = {
                    "level": record["level"].name,
                    "message": record["message"],
                    "timestamp": str(record["time"]),
                    "module": record["module"],
                    "line": record["line"]
                }

                # authorization headers
                headers = {
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                }

                # send POST request to BetterStack with the log payload
                async with self.session.post(self.url, json=payload, headers=headers) as resp:
                    if resp.status >= 400:
                        print(f"[Logail Error] {resp.status} - {await resp.text()}")
            except Exception as e:
                print(f"[Async Log Error] {e}")

    async def write(self, message):
        """
        Coroutine called by Loguru for every log message.
        Puts the message into the queue to be processed asynchronously by _send_logs().
        """
        await self.queue.put(message)

    async def start(self):
        self.task = asyncio.create_task(self._send_logs())

    async def stop(self):
        if self.session:
            await self.session.close()

        if self.task:
            self.task.cancel()
