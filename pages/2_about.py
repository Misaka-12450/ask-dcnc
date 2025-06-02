import os

import streamlit as st

BASE_DIR = os.path.join( os.path.dirname( __file__ ), ".." )
with open( os.path.join( BASE_DIR, "readme.md" ), encoding = "utf-8" ) as f:
    readme = f.read( )

# st.set_page_config(
#         page_title = "GitHub - DCNC Advisor",
#         page_icon = "static/images/favicon.png",
#         )
st.logo( "static/images/logo.png" )

st.link_button(
    "GitHub",
    "https://www.github.com/misaka-12450/cosc1111_2502_a3",
    type = "primary",
    icon = ":material/fork_right:",
)

st.markdown( readme )
