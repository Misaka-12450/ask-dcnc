import boto3
import os

from langchain_community.chat_models import BedrockChat
from langchain_huggingface import HuggingFaceEmbeddings as SentenceTransformerEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

# Data
BASE_DIR = os.path.dirname(__file__)
SYSTEM_PROMPT_PATH = os.path.normpath(
    os.path.join(BASE_DIR, "../data/system_prompt.md")
)

# Bedrock - Load environment from Docker env
REGION = os.getenv("REGION")
MODEL_ID = os.getenv("MODEL_ID")
IDENTITY_POOL_ID = os.getenv("IDENTITY_POOL_ID")
USER_POOL_ID = os.getenv("USER_POOL_ID")
APP_CLIENT_ID = os.getenv("APP_CLIENT_ID")
USERNAME = os.getenv("COGNITO_USERNAME")
PASSWORD = os.getenv("COGNITO_PASSWORD")

# LLM
TEMPERATURE = os.getenv("TEMPERATURE")
TOP_P = os.getenv("TOP_P")
MAX_TOKENS = os.getenv("MAX_TOKENS")

# FAISS
INDEX_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "../faiss_index")
)
CHUNK_SIZE = os.getenv("CHUNK_SIZE")
CHUNK_OVERLAP = os.getenv("CHUNK_OVERLAP")


# === Helper: Get AWS Credentials === #
def get_credentials(username, password):
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


# === Helper: Invoke Claude via Bedrock === #
# def invoke_bedrock(messages, max_tokens=640, temperature=0.3, top_p=0.9):
#     credentials = get_credentials(USERNAME, PASSWORD)
#     with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
#         system_prompt = f.read()
#
#     bedrock_runtime = boto3.client(
#         "bedrock-runtime",
#         region_name=REGION,
#         aws_access_key_id=credentials["AccessKeyId"],
#         aws_secret_access_key=credentials["SecretKey"],
#         aws_session_token=credentials["SessionToken"],
#     )
#
#     payload = {
#         "anthropic_version": "bedrock-2023-05-31",
#         "max_tokens": max_tokens,
#         "temperature": temperature,
#         "top_p": top_p,
#         "system": system_prompt,  # Separate system prompt from user prompt
#         "messages": messages  # Add context
#     }
#
#     response = bedrock_runtime.invoke_model(
#         body=json.dumps(payload),
#         modelId=MODEL_ID,
#         contentType="application/json",
#         accept="application/json"
#     )
#
#     result = json.loads(response["body"].read())
#     return result["content"][0]["text"]

def build_langchain() -> ConversationalRetrievalChain:
    creds = get_credentials(USERNAME, PASSWORD)

    bedrock_runtime = boto3.client(
        "bedrock-runtime",
        region_name=REGION,
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretKey"],
        aws_session_token=creds["SessionToken"],
    )

    with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
        system_prompt = f.read()

    llm = BedrockChat(
        client=bedrock_runtime,
        model_id=MODEL_ID,
        model_kwargs={
            "anthropic_version": "bedrock-2023-05-31",
            "system": system_prompt,  # ✅ goes here
            "temperature": 0.2,
            "top_p": 0.9,
            "max_tokens": 800,
        },
    )

    embeddings = SentenceTransformerEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    vectorstore = FAISS.load_local(INDEX_PATH, embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 6})

    memory = ConversationBufferMemory(
        memory_key="chat_history",  # field name expected by the chain
        return_messages=True,
    )

    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True,  # handy for debugging / UI
    )


def get_chain():
    return build_langchain()
