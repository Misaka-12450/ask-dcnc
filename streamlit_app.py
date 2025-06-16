import streamlit as st
import toml

import ask_dcnc.client

with open("pyproject.toml", "r", encoding="utf-8") as f:
    st.session_state.version = toml.load(f)["project"]["version"]
__version__ = st.session_state.version

pg = st.navigation(
    [
        # AskDCNC Page
        st.Page(
            page="pages/1_ask.py",
            title="AskDCNC",
            icon=":material/question_answer:",
        ),
        # About Page
        st.Page(
            page="pages/2_about.py",
            title="About",
            icon=":material/info:",
        ),
    ],
)

SITE_TITLE = "AskDCNC"

# https://github.com/streamlit/streamlit/issues/8960
st.set_page_config(
    page_title=(
        f"{pg.title} | {SITE_TITLE}" if pg.title != SITE_TITLE
        else SITE_TITLE
    ),
    page_icon="static/images/favicon.png",
    menu_items={
        'about': f"AskDCNC v{__version__}",
    },
)
st.logo("static/images/rmit_university_logo_144p.png")

pg.run()

ask_dcnc.client.get_aws_keys()  # Obtain AWS keys first thing to speed up response time
