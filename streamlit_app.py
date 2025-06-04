import streamlit as st
from dotenv import load_dotenv

load_dotenv( )
from bedrock import get_aws_keys

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
)
st.logo( "static/images/rmit_university_logo_144p.png" )

with st.sidebar:
    # Ask Advisor Page
    # Streamlit Pills for Answer Style Selection
    # https://docs.streamlit.io/develop/api-reference/widgets/st.pills
    if pg.title == "Ask Advisor":
        # Answer style selection
        answer_style_options = {
            "Brief": ":material/summarize: Brief",
            "Comprehensive": ":material/receipt_long: Comprehensive",
        }
        st.session_state.answer_style = st.pills(
            label = "Answer Style",
            options = answer_style_options.keys( ),
            format_func = lambda option: answer_style_options[ option ],
            default = "Brief",
        )

        # TODO: LLM model selection

        # TODO: LLM temperature selection

    # About Page
    if pg.title == "About":
        st.info(
            """
            AskDCNC is a COSC1111 Data Communications and Net-Centric Computing Assignment.
            
            Developed by Haley Wong
    
            Powered by Beer 🍺 and the Magic of AI ✨""",
        )

pg.run( )

get_aws_keys( )  # Obtain AWS keys first thing to speed up response time
