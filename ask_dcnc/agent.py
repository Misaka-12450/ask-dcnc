"""
ask_dcnc/agent.py
Functions to get the LangGraph ReAct
"""

import pathlib

import streamlit as st
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.agent_toolkits.openapi.toolkit import RequestsToolkit
from langgraph.prebuilt import create_react_agent
from loguru import logger

from ask_dcnc.db import SQLITE_URI, get_db

# Load .env file if not running in Docker
if not pathlib.Path("/.dockerenv").exists():
    from dotenv import load_dotenv

    load_dotenv()

from ask_dcnc.client import client
from ask_dcnc.html import HTMLStripRequestsWrapper

ALLOW_DANGEROUS_REQUEST = True  # For LangChain RequestsToolkit to visit the Internet


def get_agent(system_prompt: str):
    """
    Get the LangGraph ReAct agent
    :param system_prompt: System prompt for the agent
    :return: LangChain runnable for interactions
    """
    llm = client(
        llm_model=st.session_state.llm_model,
        temperature=st.session_state.llm_temperature
    )

    db = get_db(SQLITE_URI)

    tools = SQLDatabaseToolkit(
        db=db,
        llm=llm
    ).get_tools() + RequestsToolkit(
        requests_wrapper=HTMLStripRequestsWrapper(headers={}),
        allow_dangerous_requests=ALLOW_DANGEROUS_REQUEST
    ).get_tools()

    logger.success("LangChain toolkit loaded.")
    for tool in tools:
        logger.debug(f"Tool: {tool.name}, Description: {tool.description}")

    return create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt
    )
