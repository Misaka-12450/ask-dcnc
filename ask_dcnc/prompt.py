import os
import streamlit as st

BASE_DIR = os.path.join( os.path.dirname( __file__ ), ".." )
LOG_TO_CONSOLE = os.getenv( "LOG_TO_CONSOLE" )

with open( os.path.join( BASE_DIR, "prompts/system.md" ), encoding = "utf-8" ) as f:
    system_prompt = f.read( )


def get_system_prompt( ) -> str:
    try:
        if "answer_style" not in st.session_state:
            st.session_state.answer_style = "Brief"

        if LOG_TO_CONSOLE:
            print( "System prompt loaded." )

        return system_prompt.format(
            answer_style = st.session_state.answer_style,
        )
    except Exception as e:
        print( f"Error loading system prompt: {e}" )
        return ""
