"""
pages/1_ask.py
Main page where users can ask AI questions
"""

from loguru import logger
import loguru_config  # noqa: F401
import os
import pathlib
import streamlit as st

from langchain_core.messages import AIMessage

__version__ = st.session_state.version

# Check if running in Docker
if not pathlib.Path("/.dockerenv").exists():
    from dotenv import load_dotenv

    load_dotenv()
import ask_dcnc

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")

USER_AVATAR = "🧑‍🎓"
ASSISTANT_AVATAR = "static/images/logo_96p.png"

st.title(
    "AskDCNC",
    anchor=False,
    # help = "# A Data Communications and Net-Centric Computing Project"
)

with st.sidebar:
    llm_model_options = {
        "amazon.nova-pro-v1:0": "Amazon Nova Pro",
        "anthropic.claude-3-haiku-20240307-v1:0": "Claude 3 Haiku",
        "anthropic.claude-3-5-sonnet-20240620-v1:0": "Claude 3.5 Sonnet",
        "anthropic.claude-3-7-sonnet-20250219-v1:0": "Claude 3.7 Sonnet",
        "us.meta.llama4-maverick-17b-instruct-v1:0": "Llama 4 Maverick 17B Instruct",
    }
    st.session_state.llm_model = st.selectbox(
        label="LLM Model",
        options=llm_model_options.keys(),
        format_func=lambda option: llm_model_options[option],
        index=2,
        help="Some models may be unavailable",
    )

    answer_style_options = {
        "Brief": ":material/summarize: Brief",
        "Comprehensive": ":material/receipt_long: Comprehensive",
    }
    st.session_state.answer_style = st.segmented_control(
        label="Answer Style",
        options=answer_style_options.keys(),
        format_func=lambda option: answer_style_options[option],
        default="Brief",
    )

    llm_temperature_options = {
        0.0: ":material/my_location: Precise",
        0.5: ":material/balance: Balanced",
    }
    st.session_state.llm_temperature = st.segmented_control(
        label="Temperature",
        options=llm_temperature_options.keys(),
        format_func=lambda option: llm_temperature_options[option],
        default=0.5,
    )

    st.markdown("")
    st.info("Version " + __version__)

# Initial message - not a part of the chat history
with st.chat_message(name="assistant", avatar=ASSISTANT_AVATAR):
    st.markdown(
        "Hello! I am the DCNC Program and Course Advisor. "
        "You can ask me about any RMIT program or course.",
    )

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(
            name=message["role"],
            avatar=(
                    ASSISTANT_AVATAR if message["role"] == "assistant"
                    else USER_AVATAR
            ),
    ):
        st.markdown(message["content"])

# React to user input
if user_question := st.chat_input(
        "What's your question?",
):
    logger.debug(f"User question: {user_question}")

    # Returns user input
    # Display user message in chat message container
    with st.chat_message(name="user", avatar=USER_AVATAR):
        st.markdown(user_question)

    # Add user message to chat history
    st.session_state.messages.append(
        {"role": "user", "content": user_question},
    )
    messages = st.session_state.messages.copy()

    # Invoke the LLM with the chat history
    # Spinner indicates loading time
    # spinning_chat = st.empty()  # Placeholder spinner container
    # with spinning_chat.container():
    #     with st.chat_message(name="assistant", avatar=ASSISTANT_AVATAR):
    #         with st.spinner(text="Thinking...", show_time=True):
    #             response = ask_dcnc.invoke(
    #                 messages={"messages": messages},
    #                 system_prompt=ask_dcnc.get_system_prompt(),
    #             )
    # spinning_chat.empty()
    #
    # # Display the response
    # with st.chat_message(name="assistant", avatar=ASSISTANT_AVATAR):
    #     st.markdown(response)
    # # TODO: Stream the answer in real time
    #
    # # Add assistant response to chat history
    # if response:
    #     st.session_state.messages.append(
    #         {"role": "assistant", "content": response},
    #     )

    agent = ask_dcnc.invoke(
        system_prompt=ask_dcnc.get_system_prompt(),
    )

    stream = agent.stream(
        input={"messages": messages},
        stream_mode="values",
    )

    with st.chat_message(name="assistant", avatar=ASSISTANT_AVATAR):
        with st.spinner(text="Thinking...", show_time=True):
            with st.expander("Thoughts"):
                for step in stream:
                    if "messages" in step:
                        for message in step['messages']:
                            if isinstance(message, AIMessage):
                                response = message.content
                                st.write(response)

        st.markdown(response)

    if response:
        st.session_state.messages.append({"role": "assistant", "content": response})
