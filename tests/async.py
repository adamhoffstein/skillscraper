import asyncio
import re
from pathlib import Path
from typing import List
from skillscraper.parse import clean_text, load_keywords, read_local_text
from skillscraper.utils import benchmark


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


async def runner(descriptions: List[str]):
    tasks = []
    all_results = []
    for description in descriptions:
        tasks.append(get_keywords_task(description))
    results = await asyncio.gather(*tasks)
    all_results.extend(results)
    return all_results


@benchmark
def get_job_keywords_async(descriptions: List[str]):
    keywords = asyncio.run(runner(descriptions))
    print(keywords)


read_from = Path("output/los_angeles")

descriptions = [read_local_text(file) for file in read_from.iterdir()]
get_job_keywords_async(descriptions=descriptions)
