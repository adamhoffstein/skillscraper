from skillscraper import parse, scraper

URL = "https://www.linkedin.com/jobs/data-engineer-jobs-berlin?keywords=Data Engineer&location=Berlin, Berlin, Germany&locationId=&geoId=106967730&f_TPR=r86400&distance=25&position=1&pageNum=0"

# content = parse.read_local("sample.html")

# links = parse.get_links(content)

# for n, link in enumerate(links):
#     filename = f"posting_{n}.html"
#     time.sleep(random.uniform(0.4,9.2))
#     scraper.scrape_to_file(path=filename, url=link)


# for n in range(24):
#     content = parse.read_local(f"posting_{n}.html")
#     description = parse.get_description(content)
#     keywords = parse.get_keywords(description)

jobs = scraper.virtual_scroll_to_file(keywords="Data Engineer", location="Berlin, Berlin, Germany")
print(jobs)