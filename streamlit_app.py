# Cyber Security Course Advisor via AWS Bedrock
# Author: Cyrus Gao, extended by Xiang Li
# Updated: May 2025

import streamlit as st
from PIL import Image
from dotenv import load_dotenv
import os

load_dotenv()
import bedrock

# Data
BASE_DIR = os.path.dirname(__file__)
SYSTEM_PROMPT_PATH = os.path.normpath(
    os.path.join(BASE_DIR, "data/system_prompt.md")
)
with open(SYSTEM_PROMPT_PATH) as f:
    system_prompt = f.read()

# Files
logo = Image.open("static/images/logo.png")

st.logo(logo)
st.title("RMIT Course Advisor Bot",
         anchor=False,
         help="# A Data Communications and Net-Centric Computing Project"
         )

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
if user_question := st.chat_input(
        "Ask me about School of Computing Technologies programs and courses!"
):  # Returns user input
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(user_question)

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_question})

    # Build message list including system prompt
    all_messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages

    with st.chat_message("assistant"):
        response = bedrock.invoke_bedrock(all_messages)
    st.markdown(response)

    # Add assistant response to chat history
    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )
