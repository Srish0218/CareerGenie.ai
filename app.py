import json
import re
from io import BytesIO

import spacy
import streamlit as st

from utils.career_advisor import analyze_resume_with_ai
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
nlp = spacy.load("en_core_web_sm")

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

            career_tab, job_tab, skill_tab, resume_improvement, country_search, city_search, experience_search = st.tabs(
                [
                    "🎯 Career Information", "🔎 Job Search", "🔧 Skill Search", "📌 Resume Improvement",
                    "🌍 Search by Country", "🏙️ Search by City", "💼 Search by Experience"
                ])

            with career_tab:
                st.subheader("🎯 Career Information")
                st.markdown(career_info)

            with job_tab:
                st.subheader("🔎 Searching Jobs for You...")
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
                st.subheader("🔧 Skill-Based Search")
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

            # with country_search:
            #     st.subheader("🌍 Search Jobs by Country")
            #     country = st.text_input("Enter Country")
            #     if st.button("Search Jobs by Country"):
            #         linkedin_scraper = LinkedInScraper([], country=country)
            #         linkedin_results = linkedin_scraper.fetch_jobs()
            #         if linkedin_results and linkedin_results[0].get("jobs"):
            #             for job_item in linkedin_results[0]["jobs"]:
            #                 st.markdown(
            #                     f"- **[{job_item['title']}]({job_item['link']})** at *{job_item['company']}* "
            #                     f"({job_item['location']}) - ⏳ {job_item['posted']}"
            #                 )
            #         else:
            #             st.warning("No jobs found for this country.")
            #
            # with city_search:
            #     st.subheader("🏙️ Search Jobs by City")
            #     city = st.text_input("Enter City")
            #     if st.button("Search Jobs by City"):
            #         linkedin_scraper = LinkedInScraper([], location=city)
            #         linkedin_results = linkedin_scraper.fetch_jobs()
            #         if linkedin_results and linkedin_results[0].get("jobs"):
            #             for job_item in linkedin_results[0]["jobs"]:
            #                 st.markdown(
            #                     f"- **[{job_item['title']}]({job_item['link']})** at *{job_item['company']}* "
            #                     f"({job_item['location']}) - ⏳ {job_item['posted']}"
            #                 )
            #         else:
            #             st.warning("No jobs found for this city.")
            #
            # with experience_search:
            #     st.subheader("💼 Search Jobs by Experience Level and Job Profile")
            #     # Experience level options with assigned numbers
            #     experience_levels = {
            #         1: "Internship",
            #         2: "Entry level",
            #         3: "Associate",
            #         4: "Mid-Senior level",
            #         5: "Director",
            #         6: "Executive"
            #     }
            #
            #     # Multiselect dropdown for selecting experience levels
            #     selected_numbers = st.multiselect("Select Experience Levels", options=list(experience_levels.keys()),
            #                                      format_func=lambda x: experience_levels[x])
            #     # Display selected numbers in the required format
            #     if selected_numbers:
            #         Exp_preference = f"&f_E={'%2C'.join(map(str, selected_numbers))}"
            #
            #         # st.write("You selected:", "&f_E=", "%2C".join(map(str, selected_numbers)))
            #     else:
            #         Exp_preference = ""
            #         st.error("No Experience Preference Selected! ")
            #     # Button to trigger job search
            #     if st.button("Search for Job Profiles with Preferred Experience"):
            #         if selected_numbers:
            #             for job in jobs:
            #                 st.markdown(f"### 🔹 {job}")
            #                 linkedin_scraper = LinkedInScraper([job])
            #                 linkedin_results = linkedin_scraper.fetch_jobs(Exp_preference)
            #
            #                 with st.expander(f"📌 LinkedIn Jobs for {job}"):
            #                     if linkedin_results and linkedin_results[0].get("jobs"):
            #                         for job_item in linkedin_results[0]["jobs"]:
            #                             st.markdown(
            #                                 f"- **[{job_item['title']}]({job_item['link']})** at *{job_item['company']}* "
            #                                 f"({job_item['location']}) - ⏳ {job_item['posted']}"
            #                             )
            #                         st.markdown(f"[🔗 View More LinkedIn Jobs]({linkedin_results[0]['apply_link']})")
            #                     else:
            #                         st.warning(f"No jobs found for {job} on LinkedIn.")
            #         else:
            #             st.error("Please select at least one experience level.")

        except json.JSONDecodeError as e:
            st.error(f"⚠️ JSON parsing error: {str(e)}")
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")