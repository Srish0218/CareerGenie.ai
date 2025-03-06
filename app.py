import json
import re
from io import BytesIO

import streamlit as st

from utils.career_advisor import analyze_resume_with_ai, display_json
from utils.job_scraper import LinkedInSkillScraper, LinkedInScraper
from utils.resume_improver import improve_resume
from utils.resume_parser import extract_resume_text

# Streamlit Configuration
st.set_page_config(
    page_title="CareerGenie - AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load NLP model

st.title("📄 CareerGenie - AI Resume Analyzer")
uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])

if uploaded_file:
    file_name = uploaded_file.name  # Get file name
    file_extension = file_name.split(".")[-1].lower()
    resume_text = extract_resume_text(BytesIO(uploaded_file.getvalue()), file_extension)

    st.write(f"📂 **Uploaded File:** {file_name}")
    if st.button("Analyze Resume 📜"):
        with st.spinner("Analyzing..."):
            ai_response = analyze_resume_with_ai(resume_text)

        try:
            if not ai_response or not ai_response.content.strip():
                st.error("⚠️ AI response is empty. Please try again.")
                st.stop()

            cleaned_response = re.sub(r"```json|```", "", ai_response.content.strip())
            parsed_response = json.loads(cleaned_response)

            career_info = parsed_response.get("CareerInfo", "Career information not found.")
            jobs = parsed_response.get("JobTitle", [])
            skills = parsed_response.get("Skills", [])
            ExperienceLevel = parsed_response.get("ExperienceLevel", [])

            career_tab, job_tab, skill_tab, resume_improvement, job_outside_india, experience_search, early_applicant = st.tabs(
                [
                    "🎯 Career Information", "🔎 Job Search", "🔧 Skill Search", "📌 Resume Improvement",
                    "🌍 Jobs Outside India", "💼 Search by Experience", "Be an Early Applicant"
                ])

            with career_tab:
                st.subheader("🎯 Career Information")
                if isinstance(career_info, dict):
                    display_json(career_info)  # Directly print within function
                else:
                    st.write(career_info)  # Print string normally

            with job_tab:
                st.subheader("🔎 Job Search (India)")
                if jobs:
                    for job in jobs:
                        st.markdown(f"### 🔹 {job}")
                        linkedin_scraper = LinkedInScraper([job])
                        linkedin_results = linkedin_scraper.fetch_jobs()
                        with st.expander(f"📌 LinkedIn Jobs for {job}"):
                            if linkedin_results and linkedin_results[0].get("jobs"):
                                for job_item in linkedin_results[0]["jobs"]:
                                    st.markdown(
                                        f"- **[{job_item['title']}]({job_item['link']})** at *{job_item['company']}* "
                                        f"({job_item['location']}) - ⏳ {job_item['posted']}"
                                    )
                                st.markdown(f"[🔗 View More LinkedIn Jobs]({linkedin_results[0]['apply_link']})")
                            else:
                                st.warning(f"No jobs found for {job} on LinkedIn.")
                else:
                    st.warning("No job recommendations found.")

            with skill_tab:
                st.subheader("🔧 Skill-Based Search (India)")
                if skills:
                    for skill in skills:
                        st.markdown(f"### 🔹 {skill}")
                        linkedin_scraper = LinkedInSkillScraper([skill])
                        linkedin_results = linkedin_scraper.fetch_jobs()
                        with st.expander(f"📌 LinkedIn Jobs for {skill}"):
                            if linkedin_results and linkedin_results[0].get("jobs"):
                                for job_item in linkedin_results[0]["jobs"]:
                                    st.markdown(
                                        f"- **[{job_item['title']}]({job_item['link']})** at *{job_item['company']}* "
                                        f"({job_item['location']}) - ⏳ {job_item['posted']}"
                                    )
                                st.markdown(f"[🔗 View More LinkedIn Jobs]({linkedin_results[0]['apply_link']})")
                            else:
                                st.warning(f"No jobs found for {skill} on LinkedIn.")
                else:
                    st.warning("No skills found in AI response.")

            with resume_improvement:
                st.subheader("📌 Resume Improvement Suggestions")
                st.markdown(improve_resume(resume_text))

            with job_outside_india:
                st.subheader("🌍 Jobs Outside India")
                if jobs:
                    for job in jobs:
                        st.markdown(f"### 🔹 {job}")
                        linkedin_scraper = LinkedInScraper([job])
                        linkedin_results = linkedin_scraper.fetch_jobs_OutsideIndia()
                        with st.expander(f"📌 LinkedIn Jobs for {job}"):
                            if linkedin_results and linkedin_results[0].get("jobs"):
                                for job_item in linkedin_results[0]["jobs"]:
                                    st.markdown(
                                        f"- **[{job_item['title']}]({job_item['link']})** at *{job_item['company']}* "
                                        f"({job_item['location']}) - ⏳ {job_item['posted']}"
                                    )
                                st.markdown(f"[🔗 View More LinkedIn Jobs]({linkedin_results[0]['apply_link']})")
                            else:
                                st.warning(f"No jobs found for {job} on LinkedIn.")
                else:
                    st.warning("No job recommendations found.")

            with experience_search:
                st.subheader("💼 Search Jobs by Experience Level and Job Profile")
                st.info(ExperienceLevel)

                # Experience level mapping
                experience_levels = {
                    "Internship": 1,
                    "Entry level": 2,
                    "Associate": 3,
                    "Mid-Senior level": 4,
                    "Director": 5,
                    "Executive": 6
                }

                # Convert selected experience levels to corresponding numbers
                ExperienceLevels = [experience_levels[level] for level in ExperienceLevel if level in experience_levels]

                # Error handling if no experience level is selected
                if not ExperienceLevels:
                    st.error("No Experience Preference Selected!")
                else:
                    for job in jobs:
                        st.markdown(f"### 🔹 {job}")

                        for exp_level, exp_code in experience_levels.items():
                            if exp_code in ExperienceLevels:
                                exp_pref = f"&f_E={exp_code}"  # Unique experience level filter
                                linkedin_scraper = LinkedInScraper([job])
                                linkedin_results = linkedin_scraper.fetch_jobs(exp_pref)

                                with st.expander(f"📌 LinkedIn Jobs for {job} ({exp_level})"):
                                    if linkedin_results and linkedin_results[0].get("jobs"):
                                        for job_item in linkedin_results[0]["jobs"]:
                                            st.markdown(
                                                f"- **[{job_item['title']}]({job_item['link']})** at *{job_item['company']}* "
                                                f"({job_item['location']}) - ⏳ {job_item['posted']}"
                                            )
                                        st.markdown(f"[🔗 View More LinkedIn Jobs]({linkedin_results[0]['apply_link']})")
                                    else:
                                        st.warning(f"No jobs found for {job} at {exp_level} level.")

            with early_applicant:
                if jobs:
                    for job in jobs:
                        st.markdown(f"### 🔹 {job}")
                        linkedin_scraper = LinkedInScraper([job])
                        linkedin_results = linkedin_scraper.fetch_jobs_for_Early_Applicants()
                        with st.expander(f"📌 LinkedIn Jobs for {job}"):
                            if linkedin_results and linkedin_results[0].get("jobs"):
                                for job_item in linkedin_results[0]["jobs"]:
                                    st.markdown(
                                        f"- **[{job_item['title']}]({job_item['link']})** at *{job_item['company']}* "
                                        f"({job_item['location']}) - ⏳ {job_item['posted']}"
                                    )
                                st.markdown(f"[🔗 View More LinkedIn Jobs]({linkedin_results[0]['apply_link']})")
                            else:
                                st.warning(f"No jobs found for {job} on LinkedIn.")
                else:
                    st.warning("No job recommendations found.")





        except json.JSONDecodeError as e:
            st.error(f"⚠️ JSON parsing error: {str(e)}")
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")