import logging
import os

import boto3
import streamlit as st
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain_aws import ChatBedrock

from .sql import get_sql_agent

BASE_DIR = os.path.join( os.path.dirname( __file__ ), ".." )

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

LOG_TO_CONSOLE = os.getenv( "LOG_TO_CONSOLE" )


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


@st.cache_resource( ttl = 45 * 60 )
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

    langchain_messages = [ ]
    langchain_messages.append( SystemMessage( content = system_prompt ) )
    if LOG_TO_CONSOLE:
        print( f"System message: {system_prompt}" )
    for message in messages:
        role = message.get( "role" )
        content = message.get( "content", "" )
        if role == "user":
            langchain_messages.append( HumanMessage( content = content ) )
            if LOG_TO_CONSOLE:
                print( f"User message: {content}" )
        elif role == "assistant":
            langchain_messages.append( AIMessage( content = content ) )
            if LOG_TO_CONSOLE:
                print( f"Assistant message: {content}" )

    agent = get_sql_agent( llm )

    response = agent.run( input = langchain_messages )
    if LOG_TO_CONSOLE:
        print( f"Response message: {response}" )
    return response
