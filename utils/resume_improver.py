import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI

gemini_api_key = st.secrets["GEMINI_API_KEY"]


def improve_resume(resume_text):
    """Use AI to enhance resume content and suggest improvements."""
    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=gemini_api_key)

    prompt = f"""
    You are an AI Resume Improvement Expert. Analyze the resume below and suggest:
    - Better formatting for ATS (Applicant Tracking System)
    - Grammar improvements
    - More powerful wording for achievements
    - Skill enhancements

    Resume: {resume_text}
    """
    response = model.invoke(prompt)
    return response.content
