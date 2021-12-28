from skillscraper.scraper import Scraper, get_job_keywords

LOCATION = "nyc"
KEYWORDS = "Data Engineer"

job_scraper = Scraper(location=LOCATION, keywords=KEYWORDS)

descriptions = job_scraper.get_job_data()

results = get_job_keywords(descriptions=descriptions, location=LOCATION)
