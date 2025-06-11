"""
pages/1_ask.py
Main page where users can ask AI questions
"""

from loguru import logger
import loguru_config  # noqa: F401
import os
import pathlib
import streamlit as st
from datetime import datetime
from langchain_core.messages import AIMessage
from ask_dcnc import get_agent, get_system_prompt, get_time_str

__version__ = st.session_state.version

# Load .env file if not running in Docker
if not pathlib.Path("/.dockerenv").exists():
    from dotenv import load_dotenv

    load_dotenv()

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")

USER_AVATAR = "🧑‍🎓"
ASSISTANT_AVATAR = "static/images/logo_96p.png"

st.title(body="AskDCNC", anchor=False)

# TODO: Persistent state for LLM model, answer style, and temperature
# if "llm_model" not in st.session_state:
#     st.session_state.llm_model = "anthropic.claude-3-5-sonnet-20240620-v1:0"
# if "answer_style" not in st.session_state:
#     st.session_state.answer_style = "Brief"
# if "llm_temperature" not in st.session_state:
#     st.session_state.llm_temperature = 0.5

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
        help="Claude 3.5 Sonnet is recommended for accuracy. Some models may be unavailable."
    )

    answer_style_options = {
        "Brief": ":material/summarize: Brief",
        "Comprehensive": ":material/receipt_long: Comprehensive"
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
        help="Temperature controls the creativity of the model's responses.",
    )

    st.divider()
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

# Initialise thought history
if "thoughts" not in st.session_state:
    st.session_state.thoughts = []
if "thought_times" not in st.session_state:
    st.session_state.thought_times = []

# Display chat and thought history
i = 0
for message in st.session_state.messages:
    if message["role"] == "user":
        avatar = USER_AVATAR
    else:
        avatar = ASSISTANT_AVATAR
    with st.chat_message(name=message["role"], avatar=avatar):
        if message["role"] == "assistant":
            if st.session_state.thoughts[i][0]:
                with st.expander(get_time_str(st.session_state.thought_times[i])):
                    for thought in st.session_state.thoughts[i]:
                        st.write(thought)
            i += 1
        st.markdown(message["content"])

# Answer user question
if user_question := st.chat_input(
        "What's your question?",
):
    start_time = datetime.now()
    logger.success(f"User question: {user_question}")

    # Display user message in chat message container
    with st.chat_message(name="user", avatar=USER_AVATAR):
        st.markdown(user_question)
        st.empty()

    # Add user message to chat history
    st.session_state.messages.append(
        {"role": "user", "content": user_question},
    )
    messages = st.session_state.messages.copy()

    # Get LangGraph prebuilt ReAct agent
    agent = get_agent(
        system_prompt=get_system_prompt(),
    )

    # Get LLM response
    stream = agent.stream(
        input={"messages": messages},
        stream_mode="values",
    )

    # Display "thoughts" box while the user waits
    temp_container = st.empty()
    st.session_state.thoughts.append([])
    with temp_container.container():
        with st.chat_message(name="assistant", avatar=ASSISTANT_AVATAR):
            with st.spinner("Thinking", show_time=True):
                with st.expander("Thoughts"):
                    for step in stream:
                        if "messages" in step:
                            message = step['messages'][-1]
                            logger.debug(message)
                            if isinstance(message, AIMessage):
                                response = message.content
                                st.write(response)
                                st.session_state.thoughts[-1].append(response)

    # Remove the final response from the thoughts
    st.session_state.thoughts[-1].pop()
    if not st.session_state.thoughts[-1]:
        st.session_state.thoughts[-1].append("")

    # Final response
    if response:
        # Trim the "Final Answer:" part if it exists
        if "Final Answer:" in response:
            responses = response.split("Final Answer:")
            st.session_state.thoughts[-1].append(responses[0].strip())
            response = responses[1].strip()

        # Add the final response to the chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        logger.success("Assistant response:\n" + response)

    # Display the thoughts and final response in the chat box
    end_time = datetime.now()
    temp_container.empty()
    with st.chat_message(name="assistant", avatar=ASSISTANT_AVATAR):
        time_diff = end_time - start_time
        if st.session_state.thoughts[-1][0]:
            with st.expander(get_time_str(time_diff)):
                for thought in st.session_state.thoughts[-1]:
                    st.write(thought)
        st.markdown(response)
        st.session_state.thought_times.append(time_diff)
