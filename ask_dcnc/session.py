"""
ask_dcnc/session.py
Bedrock-related functions
"""

import logging
import os

import boto3
import streamlit as st
from langchain_aws import ChatBedrock
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langgraph.prebuilt import create_react_agent

BASE_DIR = os.path.join( os.path.dirname( __file__ ), ".." )
LOG_TO_CONSOLE = os.getenv( "LOG_TO_CONSOLE" )

MYSQL_HOST = os.getenv( "MYSQL_HOST" )
MYSQL_PORT = os.getenv( "MYSQL_PORT" )
MYSQL_DATABASE = os.getenv( "MYSQL_DATABASE" )
MYSQL_USERNAME = os.getenv( "MYSQL_USERNAME" )
MYSQL_PASSWORD = os.getenv( "MYSQL_PASSWORD" )
MYSQL_URI = f"mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

logger = logging.getLogger( __name__ )

# Bedrock - Load environment from Docker env
AWS_REGION = os.getenv( "AWS_REGION" )
AWS_IDENTITY_POOL_ID = os.getenv( "AWS_IDENTITY_POOL_ID" )
AWS_USER_POOL_ID = os.getenv( "AWS_USER_POOL_ID" )
AWS_APP_CLIENT_ID = os.getenv( "AWS_APP_CLIENT_ID" )
COGNITO_USERNAME = os.getenv( "COGNITO_USERNAME" )
COGNITO_PASSWORD = os.getenv( "COGNITO_PASSWORD" )

# LLM
BEDROCK_TOP_P = os.getenv( "BEDROCK_TOP_P" )
BEDROCK_MAX_TOKENS = os.getenv( "BEDROCK_MAX_TOKENS" )


# Cache AWS credentials using Cognito in Streamlit
# Original authors: Cyrus Gao, extended by Xiang Li
@st.cache_resource( ttl = 45 * 60, show_spinner = False )
def get_aws_keys( ) -> dict:
    idp_client = boto3.client( "cognito-idp", region_name = AWS_REGION )
    response = idp_client.initiate_auth(
        AuthFlow = "USER_PASSWORD_AUTH",
        AuthParameters = {
            "USERNAME": COGNITO_USERNAME, "PASSWORD": COGNITO_PASSWORD,
        },
        ClientId = AWS_APP_CLIENT_ID,
    )
    id_token = response[ "AuthenticationResult" ][ "IdToken" ]

    identity_client = boto3.client(
        "cognito-identity", region_name = AWS_REGION,
    )
    identity_response = identity_client.get_id(
        IdentityPoolId = AWS_IDENTITY_POOL_ID,
        Logins = {
            f"cognito-idp.{AWS_REGION}.amazonaws.com/{AWS_USER_POOL_ID}": id_token,
        },
    )

    creds_response = identity_client.get_credentials_for_identity(
        IdentityId = identity_response[ "IdentityId" ],
        Logins = {
            f"cognito-idp.{AWS_REGION}.amazonaws.com/{AWS_USER_POOL_ID}": id_token,
        },
    )

    creds = creds_response[ "Credentials" ]
    if LOG_TO_CONSOLE:
        print( f"Credentials obtained: {creds}" )
    return creds


# Bedrock Client
# https://python.langchain.com/api_reference/aws/chat_models/langchain_aws.chat_models.bedrock.ChatBedrock.html
@st.cache_resource( ttl = 45 * 60, show_spinner = False )
def get_client(
        llm_model: str,
        temperature: float,
        credentials: dict,
) -> ChatBedrock:
    try:
        client = ChatBedrock(
            region_name = AWS_REGION,
            aws_access_key_id = credentials[ "AccessKeyId" ],
            aws_secret_access_key = credentials[ "SecretKey" ],
            aws_session_token = credentials[ "SessionToken" ],
            model_id = llm_model,
            temperature = temperature,
            max_tokens = int( BEDROCK_MAX_TOKENS ),
            model_kwargs = {
                "top_p": float( BEDROCK_TOP_P ),
            },
        )
    except Exception as e:
        if e.response[ "Error" ][ "Code" ] == "ExpiredTokenException":
            get_aws_keys.clear( )
            credentials = get_aws_keys( )
            client = get_client( temperature, credentials )
        else:
            raise
    return client


@st.cache_resource( ttl = 45 * 60, show_spinner = False )
def client(
        llm_model: str,
        temperature: float,
) -> ChatBedrock:
    credentials = get_aws_keys( )
    # Handle ExpiredTokenException error
    llm = get_client(
        llm_model = llm_model,
        temperature = temperature, credentials = credentials,
    )
    if LOG_TO_CONSOLE:
        print(
            f"""
LLM loaded: {llm_model}, 
Temperature: {temperature},
Top P: {BEDROCK_TOP_P}, 
Max Tokens: {BEDROCK_MAX_TOKENS}.
""",
        )
    return llm


# https://python.langchain.com/docs/concepts/messages/
def invoke( messages, system_prompt: str ) -> str:
    llm = client(
        llm_model = st.session_state.llm_model,
        temperature = st.session_state.llm_temperature,
    )

    db = SQLDatabase.from_uri(
        MYSQL_URI,
        max_string_length = 6144, )

    tools = SQLDatabaseToolkit(
        db = db,
        llm = llm,
        verbose = LOG_TO_CONSOLE,
    ).get_tools( )

    if LOG_TO_CONSOLE:
        for tool in tools:
            print( f"Tool: {tool.name}, Description: {tool.description}" )

    agent = create_react_agent(
        model = llm,
        tools = tools,
        prompt = system_prompt,
    )

    # agent.invoke() returns a json
    answer = agent.invoke(
        input = messages,
    )[ "messages" ][ -1 ].content

    if "Final Answer:" in answer:
        answer = answer.split( "Final Answer:", 1 )[ 1 ].strip( )

    return answer
