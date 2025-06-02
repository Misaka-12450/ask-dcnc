import streamlit as st

st.logo( "static/images/logo.png" )

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

with st.sidebar:
    st.info(
        """
           Developed by Haley Wong

           Powered by Beer 🍺 and the Magic of AI ✨""",
    )

pg.run( )
