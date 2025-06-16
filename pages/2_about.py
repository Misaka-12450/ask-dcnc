"""
pages/2_about.py
Link to GitHub repository
"""

import os
import streamlit as st
import streamlit.components.v1 as components

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
with open(os.path.join(BASE_DIR, "readme.md"), encoding="utf-8") as f:
    readme = f.read()

with st.sidebar:
    st.info(
        """
        AskDCNC is a COSC1111 Data Communications and Net-Centric Computing Assignment.

        Developed by Haley Wong

        Powered by the Magic of AI ✨""",
    )

components.html(
    """
    <!-- Place this tag in your head or just before your close body tag. -->
    <script async defer src="https://buttons.github.io/buttons.js"></script>
    <!-- Place this tag where you want the button to render. -->
    <a class="github-button"
       href="https://github.com/Misaka-12450/ask-dcnc"
       prompts-color-scheme="no-preference: light; light: light; dark: dark;"
       prompts-size="large"
       aria-label="GitHub">
        GitHub Repository
    </a>
    """,
)

st.markdown(readme)
