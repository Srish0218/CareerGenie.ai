from urllib.parse import quote_plus

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
    BASE_URL_jobs = "https://www.linkedin.com/jobs/search/?keywords="
    BASE_URL_people = "https://www.linkedin.com/search/results/people/?keywords="

    def fetch_jobs(self, Exp_Level=None):
        """Scrape LinkedIn job postings only in India."""
        all_jobs = []
        session = requests.Session()
        india_geo_id = "102713980"  # LinkedIn Geo ID for India

        for job_title in self.search_terms:
            job_encoded = quote_plus(job_title)
            linkedin_url = f"{self.BASE_URL_jobs}{job_encoded}&geoId={india_geo_id}"

            if Exp_Level:
                linkedin_url += f"&exp={quote_plus(Exp_Level)}"

            try:
                response = session.get(linkedin_url, headers=self.HEADERS, timeout=10)
                response.raise_for_status()  # Handle HTTP errors
            except requests.exceptions.RequestException as e:
                print(f"Error fetching {linkedin_url}: {e}")
                continue

            jobs_list = []
            soup = BeautifulSoup(response.text, "html.parser")
            jobs = soup.select("div.base-card")[:10]

            for job in jobs:
                title_tag = job.find("h3")
                title = title_tag.get_text(strip=True) if title_tag else "No Title"
                if "**" in title:
                    title = "Position Name Hidden by LinkedIn (click to know more)"

                company_tag = job.find("h4")
                company = company_tag.get_text(strip=True) if company_tag else "Unknown Company"
                if "**" in company:
                    company = "Company Name Hidden"

                location_tag = job.select_one("span.job-search-card__location")
                location = location_tag.get_text(strip=True) if location_tag else "No Location"

                time_tag = job.find("time")
                posted_time = time_tag.get_text(strip=True) if time_tag else "Unknown Time"

                link_tag = job.find("a")
                link = link_tag["href"] if link_tag and link_tag.has_attr("href") else "No Link"

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

    def fetch_jobs_OutsideIndia(self, Exp_Level=None):
        """Scrape LinkedIn job postings only in India."""
        all_jobs = []
        session = requests.Session()

        for job_title in self.search_terms:
            job_encoded = quote_plus(job_title)
            linkedin_url = f"{self.BASE_URL_jobs}{job_encoded}"

            if Exp_Level:
                linkedin_url += f"&exp={quote_plus(Exp_Level)}"

            try:
                response = session.get(linkedin_url, headers=self.HEADERS, timeout=10)
                response.raise_for_status()  # Handle HTTP errors
            except requests.exceptions.RequestException as e:
                print(f"Error fetching {linkedin_url}: {e}")
                continue

            jobs_list = []
            soup = BeautifulSoup(response.text, "html.parser")
            jobs = soup.select("div.base-card")[:10]

            for job in jobs:
                title_tag = job.find("h3")
                title = title_tag.get_text(strip=True) if title_tag else "No Title"
                if "**" in title:
                    title = "Position Name Hidden by LinkedIn (click to know more)"

                company_tag = job.find("h4")
                company = company_tag.get_text(strip=True) if company_tag else "Unknown Company"
                if "**" in company:
                    company = "Company Name Hidden"

                location_tag = job.select_one("span.job-search-card__location")
                location = location_tag.get_text(strip=True) if location_tag else "No Location"

                time_tag = job.find("time")
                posted_time = time_tag.get_text(strip=True) if time_tag else "Unknown Time"

                link_tag = job.find("a")
                link = link_tag["href"] if link_tag and link_tag.has_attr("href") else "No Link"

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




    def fetch_people(self, Exp_Level=""):
        """Scrape LinkedIn People profiles with specific experience levels."""
        all_people = []

        experience_levels = {
            "Internship": 1,
            "Entry level": 2,
            "Associate": 3,
            "Mid-Senior level": 4,
            "Director": 5,
            "Executive": 6
        }

        for job_title in self.search_terms:
            job_results = {"job_title": job_title, "people": []}

            for exp_level, exp_code in experience_levels.items():
                linkedin_url = f"{self.BASE_URL_people}{job_title.replace(' ', '%20')}&f_E={exp_code}&origin=SWITCH_SEARCH_VERTICAL&sid=5GE"
                response = requests.get(linkedin_url, headers=self.HEADERS)

                people_list = []
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    people = soup.find_all("div", class_="reusable-search__entity-result")[:10]

                    for person in people:
                        name = person.find("span", class_="entity-result__title-text").get_text(
                            strip=True) if person.find("span", class_="entity-result__title-text") else "No Name"
                        position = person.find("div", class_="entity-result__primary-subtitle").get_text(
                            strip=True) if person.find("div",
                                                       class_="entity-result__primary-subtitle") else "No Position"
                        location = person.find("div", class_="entity-result__secondary-subtitle").get_text(
                            strip=True) if person.find("div",
                                                       class_="entity-result__secondary-subtitle") else "No Location"
                        profile_link = person.find("a")["href"] if person.find("a") else "No Profile Link"

                        people_list.append({
                            "name": name,
                            "position": position,
                            "location": location,
                            "profile_link": f"https://www.linkedin.com{profile_link}" if "linkedin.com" not in profile_link else profile_link
                        })

                job_results["people"].append(
                    {"experience_level": exp_level, "profiles": people_list, "search_link": linkedin_url})

            all_people.append(job_results)

        return all_people


class LinkedInSkillScraper(LinkedInScraper):
    """Scraper for LinkedIn jobs based on skills."""
    def __init__(self, skills):
        super().__init__(skills)
