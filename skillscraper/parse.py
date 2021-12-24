import re
import pandas as pd
from typing import List
from importlib.resources import read_text
from functools import lru_cache
from bs4 import BeautifulSoup
from skillscraper.log import logger


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
    logger.info(f"Loading keywords from {path}")
    data = read_text(__package__, path)
    return data.split("\n")


def get_keywords(description: str):
    keyword_paths = ["keywords.txt", "aws.txt"]
    keywords = []
    for path in keyword_paths:
        keywords.extend(load_keywords(path))
    keywords = " | ".join(list(set(keywords)))
    # for regex in patterns:
    return [
        i.lower() for i in re.findall(keywords, description, re.IGNORECASE)
    ]


def group_keywords(keywords: List[str]):
    df = pd.DataFrame({"keyword": keywords})
    df["keyword"] = df["keyword"].str.strip()
    df["occurs"] = 1
    return (
        df.groupby("keyword", as_index=False)
        .agg({"occurs": "sum"})
        .sort_values("occurs", ascending=False)
        .reset_index(drop=True)
    )
