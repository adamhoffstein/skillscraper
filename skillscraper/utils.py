import random
from typing import List
from functools import lru_cache
from importlib.resources import read_text
from pathlib import Path
from skillscraper.log import logger

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
    
