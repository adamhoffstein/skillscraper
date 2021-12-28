import asyncio
import random
import time
import aiohttp
from typing import List, Tuple
from skillscraper.utils import divide_chunks, select_random_user_agent
from skillscraper.log import logger


class AsyncClient:
    def __init__(
        self,
        requests: List[str],
        chunksize: int = 5,
        verify_html: bool = False,
        wait_time: Tuple[float] = (0.5, 9.0),
    ) -> None:
        self.user_agent = select_random_user_agent()
        self.headers = {"User-Agent": self.user_agent}
        self.request_chunks = list(divide_chunks(requests, chunksize))
        self.wait_time = wait_time
        self.all_data = []
        self.verify = verify_html

    def change_user_agent(self):
        self.user_agent = select_random_user_agent()

    def scrape(self):
        for n, chunk in enumerate(self.request_chunks):
            logger.info(f"Sending {len(chunk)} requests")
            asyncio.run(self.runner(chunk))

            # if this is not the last chunk, wait until next request
            if n + 1 < len(self.request_chunks):
                self.change_user_agent()
                self._wait()
        self.all_data = [d for d in self.all_data if d]

    def _wait(self):
        timeout = random.uniform(*self.wait_time)
        logger.info(f"Waiting for {round(timeout, 2)} seconds")
        time.sleep(timeout)

    async def fetch(self, session, url):
        tries = 0
        while tries < 5:
            try:
                async with session.get(url, allow_redirects=False) as response:
                    response = await response.text()
                    if "<!DOCTYPE html>" in response or not self.verify:
                        return response
                    logger.info(f"Retrying: {url}")
                    self._wait()
                    tries += 1
                    continue

            except Exception as e:
                logger.error(f"Failed to gather data from {url}: {e}")
                self._wait()
                tries += 1

    async def runner(self, chunk: List[str]):
        tasks = []
        async with aiohttp.ClientSession(
            headers=self.headers, trust_env=True
        ) as session:
            for url in chunk:
                tasks.append(self.fetch(session, url))

            response_data = await asyncio.gather(*tasks)
            self.all_data.extend(response_data)
            await session.close()
