import logging
import os

import streamlit as st
import pathlib

# Check if running in Docker
if not pathlib.Path( "/.dockerenv" ).exists( ):
    from dotenv import load_dotenv

    load_dotenv( )
import bedrock

BASE_DIR = os.path.join( os.path.dirname( __file__ ), ".." )

# Logging
# TODO: Log to database
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

# System Prompt
# TODO: Use a function to generate the system prompt
try:
    SYSTEM_PROMPT_PATH = os.path.normpath(
        os.path.join( BASE_DIR, "prompts/system.md" ),
    )
    with open( SYSTEM_PROMPT_PATH, encoding = "utf-8" ) as f:
        if "answer_style" not in st.session_state:
            st.session_state.answer_style = "Brief"
        if "last_answer_style" not in st.session_state:
            st.session_state.last_answer_style = st.session_state.answer_style

        original_system_prompt = f.read( )
        system_prompt = original_system_prompt.replace(
            "{answer_style}",
            st.session_state.answer_style,
        )
    if LOG_TO_CONSOLE:
        print( "System prompt loaded." )
except Exception as e:
    logger.critical( e )

USER_AVATAR = "🧑‍🎓"
ASSISTANT_AVATAR = "static/images/logo_96p.png"

st.title(
    "AskDCNC",
    anchor = False,
    # help = "# A Data Communications and Net-Centric Computing Project"
)

with st.chat_message( name = "assistant", avatar = ASSISTANT_AVATAR ):
    st.markdown(
        "Hello! I am the DCNC Program and Course Advisor. "
        "You can ask me about any RMIT program or course.",
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
        "What's your question?",
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

    # Update the system prompt
    if st.session_state.answer_style != st.session_state.last_answer_style:
        system_prompt = original_system_prompt.replace(
            "{answer_style}",
            st.session_state.answer_style,
        )
        st.session_state.last_answer_style = st.session_state.answer_style

    # Invoke the LLM with the chat history
    with st.chat_message( name = "assistant", avatar = ASSISTANT_AVATAR, ):
        try:
            response = bedrock.invoke( messages, system_prompt )
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
