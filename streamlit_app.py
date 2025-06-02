import streamlit as st

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

# https://github.com/streamlit/streamlit/issues/8960
st.set_page_config(
    page_title = (
        "About | DCNC Advisor" if pg.title == "About"
        else "DCNC Advisor"
    ),
    page_icon = "static/images/favicon.png",
)
st.logo( "static/images/rmit_university_logo_144p.png" )

with st.sidebar:
    st.info(
        """
        DCNC Program and Course Advisor is a COSC1111 Data Communications and Net-Centric Computing Assignment.
        
        Developed by Haley Wong

        Powered by Beer 🍺 and the Magic of AI ✨""",
    )

pg.run( )
