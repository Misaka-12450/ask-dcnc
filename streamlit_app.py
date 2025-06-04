import streamlit as st
from dotenv import load_dotenv
import toml

with open( "pyproject.toml", "r", encoding = "utf-8" ) as f:
    st.session_state.version = toml.load( f )[ "project" ][ "version" ]
__version__ = st.session_state.version

load_dotenv( )
from ask_dcnc import get_aws_keys

pg = st.navigation(
    [
        # Ask Advisor Page
        st.Page(
            "pages/1_ask.py",
            title = "Ask Advisor",
            icon = ":material/question_answer:",
        ),
        # About Page
        st.Page(
            "pages/2_about.py",
            title = "About",
            icon = ":material/info:",
        ),
    ],
)

SITE_TITLE = "AskDCNC"

# https://github.com/streamlit/streamlit/issues/8960
st.set_page_config(
    page_title = (
        "About | " + SITE_TITLE if pg.title == "About"
        else SITE_TITLE
    ),
    page_icon = "static/images/favicon.png",
    menu_items = {
        'about': f"AskDCNC v{__version__}",
    },
)
st.logo( "static/images/rmit_university_logo_144p.png" )

pg.run( )

get_aws_keys( )  # Obtain AWS keys first thing to speed up response time
