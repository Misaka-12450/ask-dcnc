# Cyber Security Course Advisor via AWS Bedrock
# Author: Cyrus Gao, extended by Xiang Li
# Updated: May 2025

import streamlit as st
from PIL import Image
import os
import logging
from dotenv import load_dotenv

load_dotenv()
import bedrock

# Logging
BASE_DIR = os.path.dirname( __file__ )
LOGGING_LEVEL = os.getenv( "LOGGING_LEVEL", "INFO" )
LOG_TO_CONSOLE = os.getenv( "LOG_TO_CONSOLE" )
# LOG_PATH = os.path.normpath(
#     os.path.join(BASE_DIR, os.getenv("LOG_PATH"))
# )
# if os.path.exists(LOG_PATH):
#     timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
#     os.rename(LOG_PATH, f"{LOG_PATH}.{timestamp}")
logging.basicConfig(
        level = logging.INFO,
        format = "%(asctime)s %(levelname)s %(name)s %(message)s"
        )
logger = logging.getLogger( __name__ )

# Files
logo = Image.open( "static/images/logo.png" )

st.logo( logo )
st.title(
        "RMIT Course Advisor Bot",
        anchor = False,
        help = "# A Data Communications and Net-Centric Computing Project"
        )

# Initialize chat history
if "messages" not in st.session_state:
    try:
        st.session_state.messages = [ ]
    except Exception as e:
        logger.error( e )
        st.error( f"\u274C Error: {str( e )}" )

# Display chat messages from history on app rerun
try:
    for message in st.session_state.messages:
        with st.chat_message( message[ "role" ] ):
            st.markdown( message[ "content" ] )
except Exception as e:
    logger.error( e )
    st.error( f"\u274C Error: {str( e )}" )

# React to user input
if user_question := st.chat_input(
        "Ask me about School of Computing Technologies programs and courses!"
        ):
    try:
        # Returns user input
        # Display user message in chat message container
        with st.chat_message( "user" ):
            st.markdown( user_question )

        # Add user message to chat history
        st.session_state.messages.append( { "role": "user", "content": user_question } )
        messages = [ ] + st.session_state.messages

        with st.chat_message( "assistant" ):
            response = bedrock.invoke_bedrock( messages )
            # response = bedrock.ask_sql_agent(user_question)
        st.markdown( response )

        # Add assistant response to chat history
        st.session_state.messages.append( { "role": "assistant", "content": response } )

    except Exception as e:
        logger.error( e )
        st.error( f"\u274C Error: {str( e )}" )
