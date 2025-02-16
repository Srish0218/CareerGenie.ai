import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
import json

gemini_api_key = st.secrets["GEMINI_API_KEY"]


def analyze_resume_with_ai(resume_text):
    """Analyze resume using Gemini AI to suggest career options."""
    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=gemini_api_key)

    prompt = f"""
    You are an AI career advisor. Analyze this resume and fill following in JSON:
    {{
        "CareerInfo": "- Detailed resume summary
                    - Job role he/she should apply in detail
                    - Recommend which skills he/she should focus"
                    - Give Ideas he/she can develop to showcase skills,
        "JobTitle": "Best job role for the user",
        "Skills": "Recommended skills to focus on"
    }}
    Important: 
    - **CareerInfo should be detailed, formatted with proper sections. Start with Summary and provide information in resume**
    - **JobTitle should include real-world IT job roles suitable for this candidate. At least 5**
    - **Skills should be core IT skills used in an IT company** (avoid general skills; focus on practical, high-value skills used in industry).

    Resume: {resume_text}
    """

    response = model.invoke(prompt)

    try:
        return response
    except json.JSONDecodeError:
        return {"Error": "Failed to parse AI response"}
