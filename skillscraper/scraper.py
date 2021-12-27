from os import confstr
import random
from typing import List
import requests
import time
from bs4 import BeautifulSoup
from requests.sessions import Request
from skillscraper.parse import get_links
from skillscraper.client import AsyncClient
from skillscraper.log import logger
from skillscraper.utils import select_random_user_agent

BASE_URL = (
    "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
)


def request_descriptions(urls: List[str], location: str):
    client = AsyncClient(requests=urls)
    client.scrape()
    logger.info(client.all_data)
    for n, data in enumerate(client.all_data):
        extract_to_file(f"output/{location}/result_{n}.txt", data)


def extract_to_file(path: str, data: str) -> None:
    logger.debug(f"Extracting text from div with {len(data)} characters")
    soup = BeautifulSoup(data, "html.parser")
    if content := soup.find(
        "div",
        {
            "class": "show-more-less-html__markup show-more-less-html__markup--clamp-after-5"
        },
    ):
        with open(path, "w") as file:
            file.write(content.text)
    else:
        logger.error(f"Unable to find any description.")
        with open(path.replace(".txt", "_error.txt"), "w") as file:
            file.write(data)


def virtual_scroll_to_file(keywords: str, location: str, pages: int = 3) -> None:
    geo_ids = {
        "New+York,+New+York,+United+States": "102571732",
        "Berlin, Berlin, Germany": "106967730",
    }
    job_links = []
    s = requests.session()
    s.keep_alive = False
    headers = {"User-Agent": select_random_user_agent()}
    while len(job_links) == 0:
        for i in range(0, 25, 25 * pages):
            search_params = {
                "keywords": keywords,
                "location": location,
                "geoId": geo_ids[location],
                # Recency
                "f_TPR": "r86400",
                "distance": "25",
                "position": "1",
                "pageNum": "0",
                "start": i,
            }
            req = Request(
                "GET", BASE_URL, params=search_params, headers=headers
            )
            logger.info(f"Preparing to send request to : {req.__dict__}")
            req = s.prepare_request(req)
            soup = BeautifulSoup(s.send(req).content, "html.parser")
            links = get_links(soup)
            time.sleep(random.uniform(0.4, 9.2))
            logger.info(f"Added {len(links)} links.")
            job_links.extend(links)
        return list(set(job_links))
