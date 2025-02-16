# app.py
import streamlit as st
import json
import re
from io import BytesIO
from utils.career_advisor import analyze_resume_with_ai
from utils.resume_improver import improve_resume
from utils.job_scraper import LinkedInScraper, LinkedInSkillScraper
from utils.resume_parser import extract_resume_text

st.set_page_config(page_title="CareerGenie", layout="wide")

st.title("📄 CareerGenie - AI Resume Analyzer")
st.write("Upload your resume (PDF/DOCX), and let AI suggest careers, salaries, and improvements.")

uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])

if uploaded_file:
    file_extension = uploaded_file.name.split(".")[-1].lower()
    resume_text = extract_resume_text(BytesIO(uploaded_file.getvalue()), file_extension)

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

            career_tab, job_tab, skill_tab, resume_improvement = st.tabs([
                "🎯 Career Information", "🔎 Job Search", "🔧 Skill Search", "📌 Resume Improvement"
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
                    st.warning("No job recommendations found. Consider entering a job title manually.")

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
                    st.warning("No skills found in AI response. Try adding skills manually.")

            with resume_improvement:
                st.subheader("📌 Resume Improvement Suggestions")
                st.markdown(improve_resume(resume_text))

        except json.JSONDecodeError as e:
            st.error(f"⚠️ JSON parsing error: {str(e)}")
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")