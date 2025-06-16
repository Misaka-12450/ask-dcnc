import os

import streamlit as st
from langchain_community.utilities import SQLDatabase

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
SQLITE_URI = f"sqlite:///{BASE_DIR}/data/dcnc.sqlite"


@st.cache_resource(show_spinner=False)
def get_db(uri: str) -> SQLDatabase:
    """
    Instantiate a SQLDatabase object and cache it
    :param uri: SQLAlchemy URI for the database
    :return: SQLDatabase object
    """
    return SQLDatabase.from_uri(
        uri,
        max_string_length=6144)
