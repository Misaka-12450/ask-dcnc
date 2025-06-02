import logging
import os

import boto3
import streamlit as st
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain_aws import ChatBedrock
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain.agents import initialize_agent, AgentType

# from langgraph.prebuilt import create_react_agent
# from pydantic_core.core_schema import ComputedField

BASE_DIR = os.path.join( os.path.dirname( __file__ ), ".." )

logger = logging.getLogger( __name__ )

# Bedrock - Load environment from Docker env
AWS_REGION = os.getenv( "AWS_REGION" )
AWS_MODEL_ID = os.getenv( "AWS_MODEL_ID" )
AWS_IDENTITY_POOL_ID = os.getenv( "AWS_IDENTITY_POOL_ID" )
AWS_USER_POOL_ID = os.getenv( "AWS_USER_POOL_ID" )
AWS_APP_CLIENT_ID = os.getenv( "AWS_APP_CLIENT_ID" )
COGNITO_USERNAME = os.getenv( "COGNITO_USERNAME" )
COGNITO_PASSWORD = os.getenv( "COGNITO_PASSWORD" )

# LLM
BEDROCK_TEMPERATURE = os.getenv( "BEDROCK_TEMPERATURE" )
BEDROCK_TOP_P = os.getenv( "BEDROCK_TOP_P" )
BEDROCK_MAX_TOKENS = os.getenv( "BEDROCK_MAX_TOKENS" )

# Database
MYSQL_HOST = os.getenv( "MYSQL_HOST" )
MYSQL_PORT = os.getenv( "MYSQL_PORT" )
MYSQL_DATABASE = os.getenv( "MYSQL_DATABASE" )
MYSQL_USERNAME = os.getenv( "MYSQL_USERNAME" )
MYSQL_PASSWORD = os.getenv( "MYSQL_PASSWORD" )
MYSQL_URI = (
    f"mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}")

LOG_TO_CONSOLE = os.getenv( "LOG_TO_CONSOLE" )

# System Prompt
try:
    SYSTEM_PROMPT_PATH = os.path.normpath(
        os.path.join( BASE_DIR, "data/system_prompt.md" ),
    )
    with open( SYSTEM_PROMPT_PATH, encoding = "utf-8" ) as f:
        system_prompt = f.read( )
    if LOG_TO_CONSOLE:
        print( "System prompt loaded." )
except Exception as e:
    logger.critical( e )


# Cache Database Connection
# https://python.langchain.com/api_reference/community/utilities/langchain_community.utilities.sql_database.SQLDatabase.html
@st.cache_resource( show_spinner = False )
def get_db( ) -> SQLDatabase:
    db = SQLDatabase.from_uri( MYSQL_URI )
    if LOG_TO_CONSOLE:
        print(
            f"Database loaded: {MYSQL_DATABASE}, tables: {db.get_usable_table_names( )}",
        )
    return db


# Build SQL Database Toolkit
# https://python.langchain.com/api_reference/community/agent_toolkits/langchain_community.agent_toolkits.sql.toolkit.SQLDatabaseToolkit.html
@st.cache_resource( show_spinner = False )
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
@st.cache_resource( show_spinner = False )
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


# Cache AWS credentials using Cognito in Streamlit
# Original authors: Cyrus Gao, extended by Xiang Li
@st.cache_resource( ttl = 55 * 60 )
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


# Cache the Bedrock client
# https://python.langchain.com/api_reference/aws/chat_models/langchain_aws.chat_models.bedrock.ChatBedrock.html
@st.cache_resource( ttl = 55 * 60 )
def client( ) -> ChatBedrock:
    credentials = get_aws_keys( )
    client = ChatBedrock(
        region_name = AWS_REGION,
        aws_access_key_id = credentials[ "AccessKeyId" ],
        aws_secret_access_key = credentials[ "SecretKey" ],
        aws_session_token = credentials[ "SessionToken" ],
        model_id = AWS_MODEL_ID,
        temperature = float( BEDROCK_TEMPERATURE ),
        max_tokens = int( BEDROCK_MAX_TOKENS ),
        model_kwargs = {
            "top_p": float( BEDROCK_TOP_P ),
        },
    )
    if LOG_TO_CONSOLE:
        print(
            f"""
LLM loaded: {AWS_MODEL_ID}, 
Temperature: {BEDROCK_TEMPERATURE}, 
Top P: {BEDROCK_TOP_P}, 
Max Tokens: {BEDROCK_MAX_TOKENS}.
""",
        )
    return client


# https://python.langchain.com/docs/concepts/messages/
@st.cache_resource( show_spinner = False )
def invoke( messages ):
    llm = client( )

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
