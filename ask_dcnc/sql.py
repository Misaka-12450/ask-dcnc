"""
ask_dcnc/sql.py
SQL-related functions for LangChain Agent
"""

import os

import pymysql  # noqa F401
import streamlit as st
from langchain.agents import AgentType, initialize_agent
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase

MYSQL_HOST = os.getenv( "MYSQL_HOST" )
MYSQL_PORT = os.getenv( "MYSQL_PORT" )
MYSQL_DATABASE = os.getenv( "MYSQL_DATABASE" )
MYSQL_USERNAME = os.getenv( "MYSQL_USERNAME" )
MYSQL_PASSWORD = os.getenv( "MYSQL_PASSWORD" )

LOG_TO_CONSOLE = os.getenv( "LOG_TO_CONSOLE" )


def get_uri(
        host: str,
        port: int,
        database: str,
        username: str,
        password: str,
) -> str:
    return f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"


# Cache Database Connection
# https://python.langchain.com/api_reference/community/utilities/langchain_community.utilities.sql_database.SQLDatabase.html
@st.cache_resource( )
def get_db( ) -> SQLDatabase:
    uri = get_uri(
        host = MYSQL_HOST,
        port = str( MYSQL_PORT ),
        database = MYSQL_DATABASE,
        username = MYSQL_USERNAME,
        password = MYSQL_PASSWORD,
    )
    db = SQLDatabase.from_uri( uri, max_string_length = 6144 )
    if LOG_TO_CONSOLE:
        print(
            f"Database loaded: {MYSQL_DATABASE}, tables: {db.get_usable_table_names( )}",
        )
    return db


# Build SQL Database Toolkit
# https://python.langchain.com/api_reference/community/agent_toolkits/langchain_community.agent_toolkits.sql.toolkit.SQLDatabaseToolkit.html
@st.cache_resource( ttl = 45 * 60 )
def get_sql_toolkit( _llm ) -> SQLDatabaseToolkit:
    db = get_db( )
    toolkit = SQLDatabaseToolkit(
        db = db,
        llm = _llm,
        verbose = LOG_TO_CONSOLE,
    )
    if LOG_TO_CONSOLE:
        print( "SQL database toolkit loaded." )
    return toolkit


# Initialize Agent
# https://python.langchain.com/api_reference/langchain/agents.html#module-langchain.agents
@st.cache_resource( ttl = 45 * 60 )
def get_sql_agent( _llm ) -> object:
    toolkit = get_sql_toolkit( _llm )
    agent = initialize_agent(
        tools = toolkit.get_tools( ),
        llm = _llm,
        # A zero shot agent that does a reasoning step before acting.
        agent_type = AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose = LOG_TO_CONSOLE,
        handle_parsing_errors = True,
    )
    if LOG_TO_CONSOLE:
        print( "SQL agent initialized." )
    return agent
