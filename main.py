from pathlib import Path
from datetime import datetime
import pandas as pd
from skillscraper import parse, scraper

LOCATION = "nyc"

jobs = scraper.virtual_scroll_to_file(
    keywords="Data+Engineer", location="New+York,+New+York,+United+States"
)

todaydate = str(datetime.utcnow().date())

scraper.request_descriptions(urls=jobs, location=LOCATION)

path = Path(f"./output/{LOCATION}/")
output_files = [p for p in path.iterdir() if p.suffix == ".txt"]

descriptions = []

keywords = []

for f in output_files:
    description = parse.read_local_text(f)
    keywords.extend(parse.get_keywords(description))
    descriptions.append(" ".join(description.split()))

df = pd.DataFrame({"descriptions": descriptions})
df["index"] = df.index
results = parse.group_keywords(keywords)

print(results.head(50))

df.to_csv(f"output/descriptions_{todaydate}.csv", index=False)
results.to_csv(f"output/results_{todaydate}.csv", index=False)
