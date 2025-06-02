import os

import streamlit as st
import streamlit.components.v1 as components

BASE_DIR = os.path.join( os.path.dirname( __file__ ), ".." )
with open( os.path.join( BASE_DIR, "readme.md" ), encoding = "utf-8" ) as f:
    readme = f.read( )

components.html(
    """
    <!-- Place this tag in your head or just before your close body tag. -->
    <script async defer src="https://buttons.github.io/buttons.js"></script>
    <!-- Place this tag where you want the button to render. -->
    <a class="github-button"
       href="https://github.com/Misaka-12450/cosc1111_2502_a3"
       data-color-scheme="no-preference: light; light: light; dark: dark;"
       data-size="large"
       aria-label="GitHub">
        GitHub Repository
    </a>
    """,
)

st.markdown( readme )
