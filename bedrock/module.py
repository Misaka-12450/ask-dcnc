import boto3
import os
import json

from langchain_aws import ChatBedrock
from langchain.schema import SystemMessage, HumanMessage, AIMessage

# from langchain_huggingface import HuggingFaceEmbeddings as SentenceTransformerEmbeddings
# from langchain_community.vectorstores import FAISS
# from langchain.chains import ConversationalRetrievalChain
# from langchain.memory import ConversationBufferMemory

# Data
BASE_DIR = os.path.dirname(__file__)
SYSTEM_PROMPT_PATH = os.path.normpath(
    os.path.join(BASE_DIR, "../data/system_prompt.md")
)
with open(SYSTEM_PROMPT_PATH) as f:
    system_prompt = f.read()

# Bedrock - Load environment from Docker env
REGION = os.getenv("REGION")
MODEL_ID = os.getenv("MODEL_ID")
IDENTITY_POOL_ID = os.getenv("IDENTITY_POOL_ID")
USER_POOL_ID = os.getenv("USER_POOL_ID")
APP_CLIENT_ID = os.getenv("APP_CLIENT_ID")
COGNITO_USERNAME = os.getenv("COGNITO_USERNAME")
COGNITO_PASSWORD = os.getenv("COGNITO_PASSWORD")

# LLM
TEMPERATURE = os.getenv("TEMPERATURE")
TOP_P = os.getenv("TOP_P")
MAX_TOKENS = os.getenv("MAX_TOKENS")

# FAISS
# all-MiniLM-L6-v2
INDEX_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "../faiss_index")
)
CHUNK_SIZE = os.getenv("CHUNK_SIZE")
CHUNK_OVERLAP = os.getenv("CHUNK_OVERLAP")


# === Helper: Get AWS Credentials === #
def get_credentials(
        username,
        password
):
    idp_client = boto3.client("cognito-idp", region_name=REGION)
    response = idp_client.initiate_auth(
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={"USERNAME": username, "PASSWORD": password},
        ClientId=APP_CLIENT_ID,
    )
    id_token = response["AuthenticationResult"]["IdToken"]

    identity_client = boto3.client("cognito-identity", region_name=REGION)
    identity_response = identity_client.get_id(
        IdentityPoolId=IDENTITY_POOL_ID,
        Logins={f"cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}": id_token},
    )

    creds_response = identity_client.get_credentials_for_identity(
        IdentityId=identity_response["IdentityId"],
        Logins={f"cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}": id_token},
    )

    return creds_response["Credentials"]


def invoke_bedrock(messages,
                   max_tokens=MAX_TOKENS,
                   temperature=TEMPERATURE,
                   top_p=TOP_P
                   ):
    credentials = get_credentials(COGNITO_USERNAME, COGNITO_PASSWORD)

    llm = ChatBedrock(
        region_name=REGION,
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretKey"],
        aws_session_token=credentials["SessionToken"],
        model_id=MODEL_ID,
        temperature=float(temperature),
        max_tokens=int(max_tokens),
        top_p=float(top_p)
    )

    langchain_messages = []
    langchain_messages.append(SystemMessage(content=system_prompt))
    for message in messages:
        role = message.get("role")
        content = message.get("content", "")
        if role == "user":
            langchain_messages.append(HumanMessage(content=content))
        elif role == "assistant":
            langchain_messages.append(AIMessage(content=content))
        else:
            # If you have any other roles or metadata, you can skip or extend here.
            continue

    response_message = llm.invoke(langchain_messages)
    return response_message.content
