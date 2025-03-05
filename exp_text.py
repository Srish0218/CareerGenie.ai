import streamlit as st

from utils.job_scraper import LinkedInScraper
jobs = ["Data Scientist", "Data analyst", "Python Developer"]
st.subheader("💼 Search Jobs by Experience Level and Job Profile")
# Experience level options with assigned numbers
experience_levels = {
    1: "Internship",
    2: "Entry level",
    3: "Associate",
    4: "Mid-Senior level",
    5: "Director",
    6: "Executive"
}

# Multiselect dropdown for selecting experience levels
selected_numbers = st.multiselect("Select Experience Levels", options=list(experience_levels.keys()),
                                 format_func=lambda x: experience_levels[x])
# Display selected numbers in the required format
if selected_numbers:
    Exp_preference = f"&f_E={'%2C'.join(map(str, selected_numbers))}"

    # st.write("You selected:", "&f_E=", "%2C".join(map(str, selected_numbers)))
else:
    Exp_preference = ""
    st.error("No Experience Preference Selected! ")
# Button to trigger job search
if st.button("Search for Job Profiles with Preferred Experience"):
    if selected_numbers:
        for job in jobs:
            st.markdown(f"### 🔹 {job}")
            linkedin_scraper = LinkedInScraper([job])
            linkedin_results = linkedin_scraper.fetch_jobs(Exp_preference)

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
        st.error("Please select at least one experience level.")