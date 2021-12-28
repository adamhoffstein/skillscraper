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


def read_local_html(path: str) -> BeautifulSoup:
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
    description = clean_text(description)
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


def clean_text(text: str) -> str:
    replacements = [
        ("^\s+|\s+$", ""),
        ("(?<=[.,])(?=[^\s])", " "),
        ("(?<=[a-z])(?=[A-Z|\d])", " "),
    ]
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text)
    return text.lower()


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
