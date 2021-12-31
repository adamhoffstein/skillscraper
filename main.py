from skillscraper import Scraper, Extractor
from skillscraper.parse import read_local_text
from pathlib import Path

LOCATION = "San Fransico, Calfornia, United States"
KEYWORDS = "Data Engineer"

job_scraper = Scraper(location=LOCATION, keywords=KEYWORDS)

descriptions = job_scraper.get_job_data(pages=1)

read_from = Path("output/los_angeles")

descriptions = [read_local_text(file) for file in read_from.iterdir()]

keyword_extractor = Extractor(
    descriptions=descriptions, target_path=Path("output/los_angeles")
)

results = keyword_extractor.grouped_keywords

print("Results:")
print(results.head(50))