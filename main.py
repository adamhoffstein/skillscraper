from pathlib import Path
from skillscraper import parse, scraper

jobs = scraper.virtual_scroll_to_file(keywords="Data Engineer", location="Berlin, Berlin, Germany")

for n, link in enumerate(jobs):
    scraper.scrape_to_file(path=f"output/posting_{n}.html", url=link)

path = Path("./output/")
output_files = [p for p in path.iterdir() if p.suffix == ".html"]

# descriptions = []

keywords = []

for f in output_files:
    content = parse.read_local(f)
    description = parse.get_description(content)
    keywords.extend(parse.get_keywords(description))

results = parse.group_keywords(keywords)
print(results.head(50))
