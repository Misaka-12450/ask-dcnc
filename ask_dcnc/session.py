"""
ask_dcnc/session.py
Bedrock-related functions
"""

import os
import boto3
import streamlit as st
from langchain_aws import ChatBedrock
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langgraph.prebuilt import create_react_agent
from loguru import logger
import loguru_config  # noqa: F401

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
MYSQL_USERNAME = os.getenv("MYSQL_USERNAME")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_URI = f"mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

# Bedrock - Load environment from Docker env
AWS_REGION = os.getenv("AWS_REGION")
AWS_IDENTITY_POOL_ID = os.getenv("AWS_IDENTITY_POOL_ID")
AWS_USER_POOL_ID = os.getenv("AWS_USER_POOL_ID")
AWS_APP_CLIENT_ID = os.getenv("AWS_APP_CLIENT_ID")
COGNITO_USERNAME = os.getenv("COGNITO_USERNAME")
COGNITO_PASSWORD = os.getenv("COGNITO_PASSWORD")

# LLM
BEDROCK_TOP_P = os.getenv("BEDROCK_TOP_P")
BEDROCK_MAX_TOKENS = os.getenv("BEDROCK_MAX_TOKENS")


# Cache AWS credentials using Cognito in Streamlit
# Original authors: Cyrus Gao, extended by Xiang Li
@st.cache_resource(ttl=45 * 60, show_spinner=False)
def get_aws_keys() -> dict:
    idp_client = boto3.client("cognito-idp", region_name=AWS_REGION)
    response = idp_client.initiate_auth(
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={
            "USERNAME": COGNITO_USERNAME, "PASSWORD": COGNITO_PASSWORD,
        },
        ClientId=AWS_APP_CLIENT_ID,
    )
    id_token = response["AuthenticationResult"]["IdToken"]

    identity_client = boto3.client(
        "cognito-identity", region_name=AWS_REGION,
    )
    identity_response = identity_client.get_id(
        IdentityPoolId=AWS_IDENTITY_POOL_ID,
        Logins={
            f"cognito-idp.{AWS_REGION}.amazonaws.com/{AWS_USER_POOL_ID}": id_token,
        },
    )

    creds_response = identity_client.get_credentials_for_identity(
        IdentityId=identity_response["IdentityId"],
        Logins={
            f"cognito-idp.{AWS_REGION}.amazonaws.com/{AWS_USER_POOL_ID}": id_token,
        },
    )

    creds = creds_response["Credentials"]
    logger.success(f"AWS credentials obtained")
    return creds


# Bedrock Client
# https://python.langchain.com/api_reference/aws/chat_models/langchain_aws.chat_models.bedrock.ChatBedrock.html
@st.cache_resource(ttl=45 * 60, show_spinner=False)
def client(
        llm_model: str,
        temperature: float,
) -> ChatBedrock:
    credentials = get_aws_keys()
    try:
        llm = ChatBedrock(
            region_name=AWS_REGION,
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretKey"],
            aws_session_token=credentials["SessionToken"],
            model_id=llm_model,
            temperature=temperature,
            max_tokens=int(BEDROCK_MAX_TOKENS),
            model_kwargs={
                "top_p": float(BEDROCK_TOP_P),
            },
        )
        logger.success("LLM client loaded.")
        logger.debug(f"LLM model: {llm_model}")
        logger.debug(f"LLM temperature: {temperature}")
        logger.debug(f"LLM top P: {BEDROCK_TOP_P}")
        logger.debug(f"LLM max Tokens: {BEDROCK_MAX_TOKENS}")
    except Exception as e:
        logger.error(f"Error loading LLM: {e}")
        if e.response["Error"]["Code"] == "ExpiredTokenException":
            get_aws_keys.clear()
            llm = client(llm_model=llm_model, temperature=temperature, )
        else:
            raise
    return llm


def get_agent(system_prompt: str):
    llm = client(
        llm_model=st.session_state.llm_model,
        temperature=st.session_state.llm_temperature,
    )

    db = SQLDatabase.from_uri(
        MYSQL_URI,
        max_string_length=6144, )

    tools = SQLDatabaseToolkit(
        db=db,
        llm=llm,
        verbose=True,
    ).get_tools()

    logger.success("SQLDatabaseToolkit loaded.")
    for tool in tools:
        logger.debug(f"Tool: {tool.name}, Description: {tool.description}")

    return create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt,
    )
