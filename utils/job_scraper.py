import requests
from bs4 import BeautifulSoup

class JobScraper:
    """Base class for job scrapers."""
    HEADERS = {"User-Agent": "Mozilla/5.0"}

    def __init__(self, search_terms):
        self.search_terms = search_terms if isinstance(search_terms, list) else [search_terms]

    def fetch_jobs(self):
        """To be implemented in child classes."""
        raise NotImplementedError("This method should be overridden by subclasses")


class LinkedInScraper(JobScraper):
    """Scraper for LinkedIn jobs."""
    BASE_URL = "https://www.linkedin.com/jobs/search/?keywords="

    def fetch_jobs(self):
        """Scrape LinkedIn job postings."""
        all_jobs = []
        for job_title in self.search_terms:
            linkedin_url = f"{self.BASE_URL}{job_title.replace(' ', '%20')}"
            response = requests.get(linkedin_url, headers=self.HEADERS)

            jobs_list = []
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                jobs = soup.find_all("div", class_="base-card")[:10]

                for job in jobs:
                    title = job.find("h3").get_text(strip=True) if job.find("h3") else "No Title"
                    company_tag = job.find("h4")
                    company = company_tag.get_text(strip=True) if company_tag else "Unknown Company"
                    company = "Company Name Hidden" if "********" in company else company
                    location = job.find("span", class_="job-search-card__location").get_text(strip=True) if job.find(
                        "span", class_="job-search-card__location") else "No Location"
                    posted_time = job.find("time").get_text(strip=True) if job.find("time") else "Unknown Time"
                    link = job.find("a")["href"] if job.find("a") else "No Link"

                    jobs_list.append({
                        "title": title,
                        "company": company,
                        "location": location,
                        "posted": posted_time,
                        "link": link
                    })

            all_jobs.append({
                "job_title": job_title,
                "source": "LinkedIn",
                "jobs": jobs_list,
                "apply_link": linkedin_url
            })

        return all_jobs


class LinkedInSkillScraper(LinkedInScraper):
    """Scraper for LinkedIn jobs based on skills."""
    def __init__(self, skills):
        super().__init__(skills)
