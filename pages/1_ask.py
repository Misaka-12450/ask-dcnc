import logging
import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv( )
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
    format = "%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger( __name__ )

USER_AVATAR = "🧑‍🎓"
ASSISTANT_AVATAR = "static/images/logo_96p.png"

st.title(
    "DCNC Program and Course Advisor",
    anchor = False,
    # help = "# A Data Communications and Net-Centric Computing Project"
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
        with st.chat_message(
                name = message[ "role" ],
                avatar = (
                        ASSISTANT_AVATAR if message[ "role" ] == "assistant"
                        else USER_AVATAR
                ),
        ):
            st.markdown( message[ "content" ] )
except Exception as e:
    logger.error( e )
    st.error( f"\u274C Error: {str( e )}" )

# React to user input
if user_question := st.chat_input(
        "Ask me about School of Computing Technologies programs and courses!",
):
    # Returns user input
    # Display user message in chat message container
    with st.chat_message( name = "user", avatar = USER_AVATAR, ):
        st.markdown( user_question )

    # Add user message to chat history
    st.session_state.messages.append(
        { "role": "user", "content": user_question },
    )
    messages = st.session_state.messages.copy( )

    with st.chat_message( name = "assistant", avatar = ASSISTANT_AVATAR, ):
        try:
            response = bedrock.invoke( messages )
            st.markdown( response )
        except Exception as e:
            logger.error( e )
            st.error( f"\u274C Error: {str( e )}" )
            response = ""

    # Add assistant response to chat history
    if response:
        st.session_state.messages.append(
            { "role": "assistant", "content": response },
        )
