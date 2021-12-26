import re
import pandas as pd
from typing import List
from bs4 import BeautifulSoup
from skillscraper.utils import read_internal_file_list
from skillscraper.log import logger


def read_local_text(path: str) -> str:
    logger.info(f"Reading {path}")
    with open(path) as fp:
        text = fp.read().rstrip()
    return text


def read_local(path: str) -> BeautifulSoup:
    logger.info(f"Reading {path}")
    with open(path) as fp:
        soup = BeautifulSoup(fp, "html.parser")
    return soup


def get_links(soup: BeautifulSoup) -> List[str]:
    links = soup.find_all("a", {"class": "base-card__full-link"})
    return [link.get("href") for link in links if link.get("href")]


def load_keywords(path: str):
    return read_internal_file_list(path)


def get_keywords(description: str):
    keyword_paths = ["keywords.txt", "aws.txt"]
    keywords = []
    for path in keyword_paths:
        keywords.extend(load_keywords(path))
    keywords = " | ".join(list(set(keywords)))
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
