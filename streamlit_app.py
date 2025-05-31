# Cyber Security Course Advisor via AWS Bedrock
# Author: Cyrus Gao, extended by Xiang Li
# Updated: May 2025

import streamlit as st
from PIL import Image

import bedrock

# Files
logo = Image.open("images/logo.png")

st.logo(logo)
st.title("RMIT Course Advisor Bot", anchor=False, help="""
# A Data Communications and Net-Centric Computing Project
""")

## Initialise one chain
if "qa_chain" not in st.session_state:
    try:
        st.session_state.qa_chain = bedrock.get_chain()
    except Exception as e:
        st.error(f"\u274C Error: {str(e)}")

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
        "Ask me about School of Computing Technologies programs and courses!"):  # Returns user input
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(user_question)

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_question})

    if "qa_chain" in st.session_state and st.session_state.qa_chain is not None:
        try:
            # Call the RAG chain
            # History is tracked by ConversationalRetrievalChain
            result = st.session_state.qa_chain.invoke({"question": user_question})
            answer = result["answer"]
            sources = result.get("source_documents", [])

            # Append message history to system prompt
            # messages = [{"role": "system", "content": SYSTEM_PROMPT},] + st.session_state.messages
            # messages = [] + st.session_state.messages

            # Call Bedrock with message history
            with st.chat_message("assistant"):
                st.markdown(answer)

            # Add assistant response to chat history
            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )

        except Exception as e:
            # If .invoke(...) itself fails, show an error message
            st.error(f"\u274C Error while calling QA chain: {e}")

    else:
        # If qa_chain never initialized, advise the user
        st.error("⚠️ Sorry, the QA chain isn’t available. Please check the logs above.")