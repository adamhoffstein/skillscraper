import asyncio
import re
import pandas as pd
from typing import List
from bs4 import BeautifulSoup
from skillscraper import utils
from skillscraper.utils import TODAY_DATE, read_internal_file_list, benchmark
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


async def load_keywords(path: str):
    return read_internal_file_list(path)

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
async def get_keywords_task(description: str):
    description = await clean_text(description)
    keyword_paths = ["keywords.txt", "aws.txt"]
    keywords = []
    for path in keyword_paths:
        keywords.extend(await load_keywords(path))
    keywords = " | ".join(list(set(keywords)))
    return [
        i.lower() for i in re.findall(keywords, description, re.IGNORECASE)
    ]


@benchmark
async def clean_text(text: str) -> str:
    replacements = [
        ("^\s+|\s+$", ""),
        ("(?<=[.,])(?=[^\s])", " "),
        ("(?<=[a-z])(?=[A-Z|\d])", " "),
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


@benchmark
async def get_keywords_task(description: str):
    description = await clean_text(description)
    keyword_paths = ["keywords.txt", "aws.txt"]
    keywords = []
    for path in keyword_paths:
        keywords.extend(await load_keywords(path))
    keywords = " | ".join(list(set(keywords)))
    return [
        i.lower() for i in re.findall(keywords, description, re.IGNORECASE)
    ]


@benchmark
async def keyword_runner(descriptions: List[str]):
    tasks = []
    for description in descriptions:
        tasks.append(get_keywords_task(description))
    results = await asyncio.gather(*tasks)
    print(results)
    return results


# @benchmark
# async def clean_text_runner(descriptions: List[str]):
#     tasks = []
#     all_results = []
#     for description in descriptions:
#         tasks.append(get_keywords_task(description))
#     results = await asyncio.gather(*tasks)
#     all_results.extend(results)
#     return all_results


@benchmark
def get_job_keywords(descriptions: List[str], target_path: str):
    keywords = asyncio.run(keyword_runner(descriptions))
    results = group_keywords(keywords)
    logger.info("Results:")
    logger.info(results.head(50))
    target_file = f"{target_path}/{TODAY_DATE}_results.csv"
    utils.create_dir_if_not_exists(target_path)
    results.to_csv(target_file, index=False)
    logger.info(f'Saved to: "{target_file}"')


class Extractor:
    def __init__(self, descriptions: List[str], target_path: str) -> None:
        self.all_keywords = []
        self.descriptions = descriptions
        self.target_path = target_path

    @property
    def clean_descriptions(self):
        loop = asyncio.get_event_loop()
        tasks = []
        for item in self.descriptions:
            tasks.append(self.clean_text_task(item))
        result = loop.run_until_complete(asyncio.gather(*tasks))
        loop.close()
        return result        


    @property
    def keywords(self):
        loop = asyncio.get_event_loop()
        tasks = []
        for item in self.clean_descriptions:
            tasks.append(self.get_keywords_task(item))
        result = loop.run_until_complete(asyncio.gather(*tasks))
        loop.close()
        return result
        

    @benchmark
    async def clean_text_task(self, text: str) -> str:
        replacements = [
            ("^\s+|\s+$", ""),
            ("(?<=[.,])(?=[^\s])", " "),
            ("(?<=[a-z])(?=[A-Z|\d])", " "),
        ]
        logger.info(f"Cleaning text from div with {len(text)} characters")
        for pattern, replacement in replacements:
            text = re.sub(pattern, replacement, text)
        return text.lower()