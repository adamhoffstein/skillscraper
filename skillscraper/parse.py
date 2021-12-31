import asyncio
from functools import cached_property
import re
import pandas as pd
from typing import List
from bs4 import BeautifulSoup
from skillscraper import utils
from skillscraper.utils import TODAY_DATE, read_internal_file_list, benchmark, flatten
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


@benchmark
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


@benchmark
def clean_text(text: str) -> str:
    replacements = [
        (r"^\s+|\s+$", ""),
        (r"(?<=[.,])(?=[^\s])", " "),
        (r"(?<=[a-z])(?=[A-Z|\d])", " "),
    ]
    logger.info(f"Cleaning text from div with {len(text)} characters")
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text)
    return text.lower()


@benchmark
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


class Extractor:
    def __init__(
        self,
        descriptions: List[str],
        target_path: str,
        keyword_paths: List[str] = ["keywords.txt", "aws.txt"],
    ) -> None:
        self.keyword_paths = keyword_paths
        self.descriptions = descriptions
        self.target_path = target_path

    @cached_property
    @benchmark
    def clean_descriptions(self):
        return [self.clean_text(d) for d in self.descriptions]

    @cached_property
    def search_keys(self):
        keywords = []
        for path in self.keyword_paths:
            keywords.extend(read_internal_file_list(path))
        return " | ".join(list(set(keywords)))

    @cached_property
    @benchmark
    def keywords(self):
        loop = asyncio.get_event_loop()
        tasks = []
        for item in self.clean_descriptions:
            tasks.append(self.get_keywords_task(item))
        result = loop.run_until_complete(asyncio.gather(*tasks))
        loop.close()
        return flatten(result)

    @cached_property
    @benchmark
    def grouped_keywords(self):
        results = group_keywords(self.keywords)
        target_file = f"{self.target_path}/{TODAY_DATE}_results.csv"
        utils.create_dir_if_not_exists(self.target_path)
        results.to_csv(target_file, index=False)
        logger.info(f'Saved to: "{target_file}"')
        return results

    @benchmark
    def clean_text(self, text: str) -> str:
        replacements = [
            (r"^\s+|\s+$", ""),
            (r"(?<=[.,])(?=[^\s])", " "),
            (r"(?<=[a-z])(?=[A-Z|\d])", " "),
        ]
        logger.info(f"Cleaning text from div with {len(text)} characters")
        for pattern, replacement in replacements:
            text = re.sub(pattern, replacement, text)
        return text.lower()

    @benchmark
    async def get_keywords_task(self, item: str):
        return [
            i.lower()
            for i in re.findall(self.search_keys, item, re.IGNORECASE)
        ]
