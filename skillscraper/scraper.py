from typing import List
import urllib
from bs4 import BeautifulSoup
from skillscraper import utils
from skillscraper.parse import get_links, extract_to_file
from skillscraper.client import AsyncClient
from skillscraper.log import logger
from skillscraper.utils import TODAY_DATE


class Scraper:
    def __init__(self, location: str, keywords: str) -> None:
        self.location = location.replace(" ", "+")
        self.keywords = keywords.replace(" ", "+")
        self.job_links = []
        self.job_descriptions = []

    @property
    def target_path(self):
        return (
            "output/" + self.location.lower().replace("+", "_").split(",")[0]
        )

    def get_job_links(self, pages: int = 3):
        search_url_base = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?"
        search_urls = []
        for i in range(0, 25 * pages, 25):
            search_params = {
                "keywords": self.keywords,
                "location": self.location,
                # Recency 86400 / 60 / 60 = 24 hours
                "f_TPR": "r86400",
                "distance": "25",
                "position": "1",
                "pageNum": "0",
                "start": i,
            }
            url = search_url_base + urllib.parse.urlencode(search_params)
            logger.info(f"Adding {url} to search queue")
            search_urls.append(url)
        client = AsyncClient(requests=search_urls)
        client.scrape()
        logger.info("Finished scraping job links from search page")
        for job in client.all_data:
            soup = BeautifulSoup(job, "html.parser")
            links = get_links(soup)
            if links:
                self.job_links.extend(links)
        if self.job_links:
            logger.info(f"Extracted {len(self.job_links)} job link(s)")

    def get_job_descriptions(self):
        client = AsyncClient(requests=self.job_links, verify_html=True)
        client.scrape()
        logger.info("Finished scraping job descriptions")
        if client.all_data:
            self.job_descriptions = client.all_data

    def get_job_data(self, pages: int = 3, save: bool = True) -> List[str]:
        self.get_job_links(pages=pages)
        self.get_job_descriptions()
        if self.job_descriptions:
            if save:
                logger.info(f"Saving job descriptions to {self.target_path}")
                utils.create_dir_if_not_exists(self.target_path)
                for n, data in enumerate(self.job_descriptions):
                    extract_to_file(
                        f"{self.target_path}/{TODAY_DATE}_{n}.txt", data
                    )
            return self.job_descriptions
        raise Exception("Scrape job returned no data")
