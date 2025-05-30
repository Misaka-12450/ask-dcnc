# Cyber Security Course Advisor via AWS Bedrock
# Author: Cyrus Gao, extended by Xiang Li
# Updated: May 2025

import streamlit as st
import json
import boto3
import os
from dotenv import load_dotenv
from PIL import Image

# Environment variables
try:
    load_dotenv()
except Exception as e:
    st.error(f"\u274C Error: {str(e)}")

# Bedrock
REGION = os.getenv("REGION")
MODEL_ID = os.getenv("MODEL_ID")
IDENTITY_POOL_ID = os.getenv("IDENTITY_POOL_ID")
USER_POOL_ID = os.getenv("USER_POOL_ID")
APP_CLIENT_ID = os.getenv("APP_CLIENT_ID")
USERNAME = os.getenv("COGNITO_USERNAME")
PASSWORD = os.getenv("COGNITO_PASSWORD")

# Files
logo = Image.open("images/logo.png")
courses_json = open("courses_data.json", "r")
courses = json.load(courses_json)
program_json = open("cyber_security_program_structure.json", "r")
structure = json.load(program_json)

# System Prompt
structure_text = ""
full_course_context = ""
SYSTEM_PROMPT = (
        "You are a helpful assistant that supports students in selecting courses from the "
        "Bachelor of Cyber Security program at RMIT (codes BP355/BP356). "
        "Recommend only from the official course list. Each course is categorized as core, capstone, minor, or elective. "
        "Use the recommended structure to suggest suitable courses based on study year and interest.\n\n"
        + structure_text
        + "\n### All Available Courses:\n"
        + full_course_context
)


# === Helper: Get AWS Credentials === #
def get_credentials(username, password):
    idp_client = boto3.client("cognito-idp", region_name=REGION)
    response = idp_client.initiate_auth(
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={"USERNAME": username, "PASSWORD": password},
        ClientId=APP_CLIENT_ID,
    )
    id_token = response["AuthenticationResult"]["IdToken"]

    identity_client = boto3.client("cognito-identity", region_name=REGION)
    identity_response = identity_client.get_id(
        IdentityPoolId=IDENTITY_POOL_ID,
        Logins={f"cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}": id_token},
    )

    creds_response = identity_client.get_credentials_for_identity(
        IdentityId=identity_response["IdentityId"],
        Logins={f"cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}": id_token},
    )

    return creds_response["Credentials"]


# === Helper: Build Prompt from JSON + Structure === #
def build_prompt(courses, user_question, structure=None):
    course_dict = {c["title"]: c for c in courses}

    structure_text = ""
    if structure and "recommended_courses" in structure:
        structure_text += "### Recommended Study Plan by Year:\n"
        for year, course_titles in structure["recommended_courses"].items():
            structure_text += f"**{year.replace('_', ' ').title()}**:\n"
            for title in course_titles:
                course = course_dict.get(title)
                if course:
                    structure_text += f"- {title} ({course['course_code']})\n"
                else:
                    structure_text += f"- {title} (not found in course list)\n"
            structure_text += "\n"

    course_list = []
    for course in courses:
        title = course.get("title", "Untitled")
        code = course.get("course_code", "N/A")
        desc = course.get("description", "No description available.")
        course_type = course.get("course_type", "N/A")
        minor = course.get("minor_track", [])
        minor_info = f", Minor: {minor[0]}" if minor else ""
        course_text = f"- {title} ({code}): {desc}\n  Type: {course_type}{minor_info}"
        course_list.append(course_text)
    full_course_context = "\n".join(course_list)

    bedrock_prompt = (
            "\n\nUser:\n" + user_question
    )
    return bedrock_prompt


# === Helper: Extract text from multiple PDFs === #
def extract_text_from_pdfs(pdf_files):
    all_text = []
    for pdf_file in pdf_files:
        try:
            reader = PdfReader(pdf_file)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    all_text.append(text.strip())
        except Exception as e:
            all_text.append(f"[Error reading file {pdf_file.name}: {str(e)}]")
    return "\n\n".join(all_text)


# === Helper: Invoke Claude via Bedrock === #
def invoke_bedrock(messages, max_tokens=640, temperature=0.3, top_p=0.9):
    credentials = get_credentials(USERNAME, PASSWORD)

    bedrock_runtime = boto3.client(
        "bedrock-runtime",
        region_name=REGION,
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretKey"],
        aws_session_token=credentials["SessionToken"],
    )

    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "messages": messages  # Add context
    }

    response = bedrock_runtime.invoke_model(
        body=json.dumps(payload),
        modelId=MODEL_ID,
        contentType="application/json",
        accept="application/json"
    )

    result = json.loads(response["body"].read())
    return result["content"][0]["text"]


st.logo(logo)
st.title("RMIT Course Advisor Bot", anchor=False, help="""
# A Data Communications and Net-Centric Computing Project
""")

# Initialize chat history
if "messages" not in st.session_state:
    try:
        st.session_state.messages = []
    except Exception as e:
        st.error(f"\u274C Error: {str(e)}")

# Display chat messages from history on app rerun
try:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
except Exception as e:
    st.error(f"\u274C Error: {str(e)}")

# React to user input
if user_question := st.chat_input("Ask me about School of Computing Technologies programs and courses!"):  # Returns user input
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(user_question)

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_question})

    # Append message history to system prompt
    # messages = [{"role": "system", "content": SYSTEM_PROMPT},] + st.session_state.messages
    messages = [] + st.session_state.messages

    # Call Bedrock with message history
    with st.chat_message("assistant"):
        response = invoke_bedrock(messages)
    st.markdown(response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
