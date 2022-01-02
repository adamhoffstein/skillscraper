import time
from datetime import datetime
import random
from typing import List
from functools import lru_cache
from importlib.resources import read_text
from pathlib import Path
from bs4 import BeautifulSoup

import pandas as pd
import requests
from skillscraper.log import logger

TODAY_DATE = str(datetime.utcnow().date())


@lru_cache
def read_internal_file(path: str) -> str:
    logger.info(f"Reading {path}")
    if text := read_text(__package__, path):
        return text
    raise Exception(f"Unable to find {path}")


@lru_cache
def read_internal_file_list(path: str) -> List[str]:
    logger.info(f"Splitting {path} to list")
    return read_internal_file(path).split("\n")


def select_random_user_agent() -> List[str]:
    return random.choice(read_internal_file_list("agents.txt"))


def divide_chunks(items: list, n: int):
    for i in range(0, len(items), n):
        yield items[i : i + n]


def create_dir_if_not_exists(path: str) -> None:
    if not Path(path).exists():
        Path(path).mkdir(parents=True)


def benchmark(func):
    def _timing(*args, **kwargs):
        start = time.perf_counter()
        r = func(*args, **kwargs)
        logger.debug(
            f"{func.__name__} execution: {round(time.perf_counter() - start, 2)} seconds"
        )
        return r

    return _timing


def flatten(t):
    return [item for sublist in t for item in sublist]


def get_proxy_table(data: str):
    logger.debug(
        f"Extracting text from html document with {len(data)} characters"
    )
    soup = BeautifulSoup(data, "html.parser")
    if content := soup.find(
        "table", {"class": "table table-striped table-bordered"}
    ):
        return str(content)
    raise Exception("Unable to find any proxies in html data")


@lru_cache
def get_proxy_list():
    url = "https://free-proxy-list.net/anonymous-proxy.html"
    logger.info(f"Getting proxies from {url}")
    response = requests.get(url)
    if response.content:
        proxy_raw = get_proxy_table(response.content)
        proxy_df = pd.read_html(proxy_raw)[0]
        proxy_df.columns = [
            c.lower().replace(" ", "_") for c in proxy_df.columns
        ]
        viable_proxies = proxy_df.loc[
            (proxy_df.anonymity == "anonymous") & (proxy_df.https == "yes")
        ]
        if not viable_proxies.empty:
            return viable_proxies.to_records(index=False)
    raise Exception("Unable to fetch data from free-proxy-list.net")
