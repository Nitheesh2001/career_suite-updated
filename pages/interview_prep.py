import streamlit as st
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
import PyPDF2
from utils.auth import authenticate_user, register_user  # Your existing auth

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="Interview Preparation AI",
    page_icon="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQJL_4deHMJLHCB-63srdgaBe2JZmiOSxlnEg&s"
)

# Configure Google Generative AI API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Session state
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "page" not in st.session_state:
    st.session_state["page"] = "login"

# ---------- INTERVIEW LOGIC ----------
def generate_interview_preparation(job_role, resume_text, job_description, num_questions):
    prompt_template = """
You are an AI assistant specializing in interview preparation. 
Please respond ONLY in the following exact JSON format:

{
  "Interview Questions": ["question1", "question2", ...],
  "Detailed Answers": {
    "question1": "answer1",
    "question2": "answer2",
    ...
  }
}

DO NOT include any explanations or notes outside the JSON.

Here is the input data:
"""
    input_data = {
        "Job Role": job_role,
        "Resume": resume_text,
        "Job Description": job_description,
        "Number of Questions": num_questions
    }
    prompt = prompt_template + json.dumps(input_data)

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# ---------- PAGES ----------
def show_login_page():
    st.title("Welcome to the Interview Preparation Tool!")
    st.subheader("Log in to access tailored resources and practice questions.")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if authenticate_user(username, password):
            st.session_state["logged_in"] = True
            st.session_state["page"] = "home"
            st.rerun()
        else:
            st.error("Invalid username or password")

    if st.button("Sign Up"):
        st.session_state["page"] = "signup"
        st.rerun()

def show_signup_page():
    st.title("Signup")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Signup"):
        if password == confirm_password:
            if register_user(username, password):
                st.success("Signup successful! Please log in.")
                st.session_state["page"] = "login"
                st.rerun()
            else:
                st.error("Signup failed. Username might already exist.")
        else:
            st.error("Passwords do not match.")

    if st.button("Back to Login"):
        st.session_state["page"] = "login"
        st.rerun()

def show_main_page():
    st.title("Interview Preparation Module")
    st.subheader("Get ready for your next job interview with tailored questions and answers")

    job_role = st.text_input("Job Role")
    uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type="pdf")
    job_description = st.text_area("Paste the Job Description")
    num_questions = st.number_input("Number of Questions", min_value=1, max_value=50, value=10, step=1)

    if st.button("Generate Interview Questions and Answers"):
        if job_role and uploaded_file and job_description:
            with st.spinner("Generating interview preparation materials..."):
                try:
                    resume_text = extract_text_from_pdf(uploaded_file)
                    response_text = generate_interview_preparation(job_role, resume_text, job_description, num_questions)

                    # Show raw Gemini output for debugging
                    st.subheader("🔍 Raw Gemini Output:")
                    st.code(response_text, language="json")

                    # Parse Gemini response
                    questions_and_answers = json.loads(response_text)

                    interview_questions = questions_and_answers.get("Interview Questions", [])[:num_questions]
                    detailed_answers = questions_and_answers.get("Detailed Answers", {})

                    st.subheader("📋 Interview Questions and Answers")
                    for i, question in enumerate(interview_questions, start=1):
                        st.write(f"**Question {i}:** {question}")
                        st.write(f"**Answer:** {detailed_answers.get(question, 'No answer provided.')}")
                        st.write("---")
                except json.JSONDecodeError:
                    st.error("❌ Gemini response is not in valid JSON format. Please check the raw output above.")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        else:
            st.warning("Please fill all the fields and upload your resume.")

# ---------- ROUTING ----------
if st.session_state["logged_in"]:
    if st.session_state["page"] == "home":
        show_main_page()
    else:
        st.session_state["page"] = "home"
        st.rerun()
else:
    if st.session_state["page"] == "login":
        show_login_page()
    elif st.session_state["page"] == "signup":
        show_signup_page()
    else:
        st.session_state["page"] = "login"
        st.rerun()
