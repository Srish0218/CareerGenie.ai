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
    BASE_URL_JOBS = "https://www.linkedin.com/jobs/search/?"
    BASE_URL_PEOPLE = "https://www.linkedin.com/search/results/people/?keywords="

    def fetch_jobs(self, Exp_Level=None, geo_id="102713980", EarlyApp=False):
        """
        Scrape LinkedIn job postings.
        :param EarlyApp:
        :param Exp_Level: Experience level filter (optional)
        :param geo_id: LinkedIn Geo ID (default: India)
        """
        all_jobs = []
        session = requests.Session()

        for job_title in self.search_terms:
            job_encoded = "&keywords=" + quote_plus(job_title)

            if EarlyApp:
                linkedin_url = f"{self.BASE_URL_JOBS}&f_EA=true{job_encoded}"
            else:
                linkedin_url = f"{self.BASE_URL_JOBS}{job_encoded}"
            if geo_id:
                linkedin_url += f"&geoId={geo_id}"
            if Exp_Level:
                linkedin_url += f"&exp={quote_plus(Exp_Level)}"

            try:
                response = session.get(linkedin_url, headers=self.HEADERS, timeout=10)
                response.raise_for_status()  # Handle HTTP errors
            except requests.exceptions.RequestException as e:
                print(f"Error fetching {linkedin_url}: {e}")
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            jobs = soup.select("div.base-card")[:10]

            jobs_list = [
                {
                    "title": job.find("h3").get_text(strip=True) if job.find("h3") else "No Title",
                    "company": job.find("h4").get_text(strip=True) if job.find("h4") else "Unknown Company",
                    "location": job.select_one("span.job-search-card__location").get_text(strip=True) if job.select_one(
                        "span.job-search-card__location") else "No Location",
                    "posted": job.find("time").get_text(strip=True) if job.find("time") else "Unknown Time",
                    "link": job.find("a")["href"] if job.find("a") and job.find("a").has_attr("href") else "No Link",
                }
                for job in jobs
            ]

            all_jobs.append({
                "job_title": job_title,
                "source": "LinkedIn",
                "jobs": jobs_list,
                "apply_link": linkedin_url
            })

        return all_jobs

    def fetch_jobs_OutsideIndia(self, Exp_Level=None):
        """Fetch LinkedIn job postings outside India."""
        return self.fetch_jobs(Exp_Level, geo_id=None)

    def fetch_jobs_for_Early_Applicants(self):
        return self.fetch_jobs(Exp_Level=None, geo_id=None, EarlyApp=True)

    def fetch_people(self):
        """Scrape LinkedIn People profiles with specific experience levels."""
        all_people = []
        session = requests.Session()

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
                linkedin_url = f"{self.BASE_URL_PEOPLE}{quote_plus(job_title)}&f_E={exp_code}&origin=SWITCH_SEARCH_VERTICAL"

                try:
                    response = session.get(linkedin_url, headers=self.HEADERS, timeout=10)
                    response.raise_for_status()
                except requests.exceptions.RequestException as e:
                    print(f"Error fetching {linkedin_url}: {e}")
                    continue

                soup = BeautifulSoup(response.text, "html.parser")
                people = soup.find_all("div", class_="reusable-search__entity-result")[:10]

                people_list = [
                    {
                        "name": person.find("span", class_="entity-result__title-text").get_text(
                            strip=True) if person.find("span", class_="entity-result__title-text") else "No Name",
                        "position": person.find("div", class_="entity-result__primary-subtitle").get_text(
                            strip=True) if person.find("div",
                                                       class_="entity-result__primary-subtitle") else "No Position",
                        "location": person.find("div", class_="entity-result__secondary-subtitle").get_text(
                            strip=True) if person.find("div",
                                                       class_="entity-result__secondary-subtitle") else "No Location",
                        "profile_link": f"https://www.linkedin.com{person.find('a')['href']}" if person.find(
                            "a") and person.find("a").has_attr("href") else "No Profile Link"
                    }
                    for person in people
                ]

                job_results["people"].append(
                    {"experience_level": exp_level, "profiles": people_list, "search_link": linkedin_url}
                )

            all_people.append(job_results)

        return all_people


class LinkedInSkillScraper(LinkedInScraper):
    """Scraper for LinkedIn jobs based on skills."""

    def __init__(self, skills):
        super().__init__(skills)
