import asyncio
import random
import time
import aiohttp
from typing import List
from skillscraper.utils import divide_chunks, select_random_user_agent
from skillscraper.log import logger

class AsyncClient:
    def __init__(self, requests: List[str], chunksize: int = 10) -> None:
        self.user_agent = select_random_user_agent()
        self.headers = {"User-Agent": self.user_agent}
        self.request_chunks = list(divide_chunks(requests, chunksize))
        self.all_data = []

    def set_user_agent(self):
        self.user_agent = select_random_user_agent() 

    def scrape(self):
        for chunk in self.request_chunks:
            logger.info(f"Sending {len(chunk)} requests")
            self.run(chunk)
            self.set_header()
            timeout = random.uniform(0.4, 9.2)
            logger.info(f"Waiting for {timeout} seconds")
            time.sleep(timeout)
    
    async def fetch(self, session, url):
        try:
            async with session.get(url) as response:
                return await response.text()
        except Exception as e:
            logger.error(f"Failed to gather data from {url}: {e}")

    async def run(self, chunk: List[str]):
        tasks = []
        async with aiohttp.ClientSession(headers=self.headers, trust_env=True) as session:
            for url in chunk:
                tasks.append(self.fetch(session, url))

            response_data = await asyncio.gather(*tasks)
            self.all_data.extend(response_data)
            await session.close()
    