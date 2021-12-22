import re
from typing import List
from importlib.resources import read_text
from functools import lru_cache
from bs4 import BeautifulSoup


def read_local(path: str) -> BeautifulSoup:
    with open(path) as fp:
        soup = BeautifulSoup(fp, "html.parser")
    return soup


def get_links(soup: BeautifulSoup) -> List[str]:
    links = soup.find_all("a", {"class": "base-card__full-link"})
    return [link.get("href") for link in links if link.get("href")]


def get_description(soup: BeautifulSoup) -> List[str]:
    description = soup.find(
        "div", {"class": "description__text description__text--rich"}
    )
    return re.sub(r"\\n", "", description.text)


@lru_cache
def load_keywords(path: str):
    print(f"Loading keywords from {path}")
    data = read_text(__package__, path)
    return data.split("\n")


def get_keywords(description: str):
    keyword_paths = ["keywords.txt", "aws.txt"]
    keywords = []
    for path in keyword_paths:
        keywords.extend(load_keywords(path))
    keywords = " | ".join(list(set(keywords)))
    # for regex in patterns:
    print(re.findall(keywords, description, re.IGNORECASE))
