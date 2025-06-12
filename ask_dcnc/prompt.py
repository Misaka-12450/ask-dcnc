import os
import streamlit as st
from loguru import logger
import loguru_config  # noqa: F401

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")


def get_system_prompt() -> str:
    try:
        with open(os.path.join(BASE_DIR, "prompts/system.md"), encoding="utf-8") as f:
            system_prompt = f.read()

        if st.session_state.answer_style == "Comprehensive":
            answer_style = "comprehensive: You should answer the question in a detailed and thorough manner, providing all relevant information and context."
        else:
            answer_style = "brief: You should summarise the answer into one or two short paragraphs."

        prompt = system_prompt.format(answer_style=answer_style)
        logger.debug(f"System prompt loaded:\n{prompt}")
        return prompt

    except Exception as e:
        logger.error(e)
        return ""
