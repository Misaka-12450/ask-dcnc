import boto3
import os
import logging
import streamlit as st

from langchain_aws import ChatBedrock
from langchain.schema import SystemMessage, HumanMessage, AIMessage

# from langchain_community.agent_toolkits import SQLDatabaseToolkit
# from langchain_community.utilities import SQLDatabase
# from langgraph.prebuilt import create_react_agent
# from pydantic_core.core_schema import ComputedField

BASE_DIR = os.path.abspath(
        os.path.join(
                os.path.dirname( __file__ ),
                ".."
                )
        )

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

LOG_TO_CONSOLE = os.getenv( "LOG_TO_CONSOLE" )

# System Prompt
try:
    SYSTEM_PROMPT_PATH = os.path.normpath(
            os.path.join( BASE_DIR, "data/system_prompt.md" )
            )
    with open( SYSTEM_PROMPT_PATH, encoding = "utf-8" ) as f:
        system_prompt = f.read()
    if LOG_TO_CONSOLE:
        print( "System prompt loaded." )
except Exception as e:
    logger.critical( e )

# Database
# try:
#     db_path = os.path.join( BASE_DIR, "data/db.sqlite" )
#     db = SQLDatabase.from_uri( f"sqlite:///{db_path}" )
#     if LOG_TO_CONSOLE:
#         print( "Database loaded." )
#         print( f"Available tables: {db.get_usable_table_names()}" )
#         for table_name in db.get_usable_table_names():
#             sample = db.run( f"SELECT * FROM {table_name} LIMIT 1;" )
#             print( f"Sample output for {table_name}: {sample}" )
# except Exception as e:
#     logger.critical( e )

# FAISS
# all-MiniLM-L6-v2
INDEX_PATH = os.path.normpath(
        os.path.join( os.path.dirname( __file__ ), "../faiss_index" )
        )
CHUNK_SIZE = os.getenv( "CHUNK_SIZE" )
CHUNK_OVERLAP = os.getenv( "CHUNK_OVERLAP" )


# === Helper: Get AWS Credentials ===
def get_credentials() -> dict:
    idp_client = boto3.client( "cognito-idp", region_name = AWS_REGION )
    response = idp_client.initiate_auth(
            AuthFlow = "USER_PASSWORD_AUTH",
            AuthParameters = { "USERNAME": COGNITO_USERNAME, "PASSWORD": COGNITO_PASSWORD },
            ClientId = AWS_APP_CLIENT_ID,
            )
    id_token = response[ "AuthenticationResult" ][ "IdToken" ]

    identity_client = boto3.client( "cognito-identity", region_name = AWS_REGION )
    identity_response = identity_client.get_id(
            IdentityPoolId = AWS_IDENTITY_POOL_ID,
            Logins = { f"cognito-idp.{AWS_REGION}.amazonaws.com/{AWS_USER_POOL_ID}": id_token },
            )

    creds_response = identity_client.get_credentials_for_identity(
            IdentityId = identity_response[ "IdentityId" ],
            Logins = { f"cognito-idp.{AWS_REGION}.amazonaws.com/{AWS_USER_POOL_ID}": id_token },
            )

    creds = creds_response[ "Credentials" ]
    if LOG_TO_CONSOLE:
        print( f"Credentials obtained: {creds}" )
    return creds


# Cache credentials instead of fetching them every time
@st.cache_resource( ttl = 55 * 60 )
def aws_credentials():
    return get_credentials()


# Cache the Bedrock client
@st.cache_resource( ttl = 55 * 60 )
def bedrock_client() -> ChatBedrock:
    credentials = aws_credentials()
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
                    }
            )
    if LOG_TO_CONSOLE:
        print(
                f"""
LLM loaded: {AWS_MODEL_ID}, 
Temperature: {BEDROCK_TEMPERATURE}, 
Top P: {BEDROCK_TOP_P}, 
Max Tokens: {BEDROCK_MAX_TOKENS}.
"""
                )
    return client


@st.cache_resource( show_spinner = False )
def invoke_bedrock( messages ):
    llm = bedrock_client()

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

    response_message = llm.invoke( langchain_messages )
    if LOG_TO_CONSOLE:
        print( f"Response message: {response_message.content}" )
    return response_message.content
