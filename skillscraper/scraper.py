import random
import requests
import time
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from requests.sessions import Request
from skillscraper.parse import get_links

BASE_URL = (
    "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
)


def scrape_to_file(path: str, url: str) -> None:
    ua = UserAgent()

    headers = {"User-Agent": ua.random}
    print(headers)

    soup = BeautifulSoup(
        requests.get(url, headers=headers).content, "html.parser"
    )

    html = soup.prettify("utf-8")

    with open(path, "w") as file:
        file.write(str(html))


def virtual_scroll_to_file(keywords: str, location: str) -> None:
    job_links = []
    s = requests.session(config={'keep_alive': False})
    ua = UserAgent()
    headers = {"User-Agent": ua.random}
    for i in range(0, 50, 25):
        search_params = {
            "keywords": keywords,
            "location": location,
            "geoId": "106967730",
            "f_TPR": "r86400",
            "distance": "25",
            "position": "1",
            "pageNum": "0",
            "start": i,
        }
        req = Request("GET", BASE_URL, params=search_params, headers=headers)
        req = s.prepare_request(req)
        soup = BeautifulSoup(s.send(req).content, "html.parser")
        links = get_links(soup)
        time.sleep(random.uniform(0.4, 9.2))
        print(f"Added {len(links)} links.")
        job_links.extend(links)
    total_links = list(set(job_links))
    print(f"Scraped {len(total_links)} total links.")
    return total_links


# def proxy_scrape_to_file(path: str, url: str) -> None:
#     req_proxy = RequestProxy(log_level=logging.ERROR)
