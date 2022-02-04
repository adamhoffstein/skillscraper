from skillscraper import Scraper, Extractor
from skillscraper.utils import TODAY_DATE
from skillscraper.parse import read_local_text
from pathlib import Path

LOCATION = "Put a location here"
KEYWORDS = "Software Engineer"

job_scraper = Scraper(location=LOCATION, keywords=KEYWORDS, use_proxy=True)

job_scraper.get_job_data(pages=1)

descriptions = [
    read_local_text(file)
    for file in Path(job_scraper.target_path).iterdir()
    if file.suffix == ".txt" and TODAY_DATE in file.name
]

keyword_extractor = Extractor(
    descriptions=descriptions, target_path=Path(job_scraper.target_path)
)

results = keyword_extractor.grouped_keywords

print("Results:")
print(results.head(50))
