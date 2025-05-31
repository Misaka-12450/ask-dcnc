import boto3
import os
import json

from langchain_aws import ChatBedrock
from langchain.schema import SystemMessage, HumanMessage, AIMessage

from langchain_huggingface import HuggingFaceEmbeddings as SentenceTransformerEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

# Bedrock - Load environment from Docker env
REGION = os.getenv("REGION")
MODEL_ID = os.getenv("MODEL_ID")
IDENTITY_POOL_ID = os.getenv("IDENTITY_POOL_ID")
USER_POOL_ID = os.getenv("USER_POOL_ID")
APP_CLIENT_ID = os.getenv("APP_CLIENT_ID")
COGNITO_USERNAME = os.getenv("COGNITO_USERNAME")
COGNITO_PASSWORD = os.getenv("COGNITO_PASSWORD")

# LLM
TEMPERATURE = float(os.getenv("TEMPERATURE"))
TOP_P = float(os.getenv("TOP_P"))
# MAX_TOKENS = int(os.getenv("MAX_TOKENS"))

# FAISS
# all-MiniLM-L6-v2
INDEX_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "../faiss_index")
)
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP"))
K = int(os.getenv("K"))


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
                   # max_tokens=MAX_TOKENS,
                   temperature=TEMPERATURE,
                   top_p=TOP_P
                   ):
    credentials = get_credentials(COGNITO_USERNAME, COGNITO_PASSWORD)
    print(f"Credentials acquired: {credentials}\n")

    llm = ChatBedrock(
        region_name=REGION,
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretKey"],
        aws_session_token=credentials["SessionToken"],
        model_id=MODEL_ID,
        temperature=temperature,
        # max_tokens=max_tokens,
        top_p=top_p,
    )

    # Load FAISS index
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = FAISS.load_local(INDEX_PATH,
                                    embeddings,
                                    allow_dangerous_deserialization=True
                                    )
    retriever = vector_store.as_retriever(search_kwargs={"k": K})

    # Build a RAG chain
    rag_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )
    print(f"RAG chain retrieved: {rag_chain}\n")

    # Convert message history to Langchain
    # Message is a list of dicts {"role": "...", "content": "..."}
    chat_history = []
    user_question = None
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content", "")
        if role == "system":
            # Pass system prompt as the very first message in history
            chat_history.append(SystemMessage(content=content))
            print(f"SystemMessage: {content}\n")
        elif role == "user":
            user_question = content
            chat_history.append(HumanMessage(content=content))
            print(f"HumanMessage: {content}\n")
        elif role == "assistant":
            chat_history.append(AIMessage(content=content))
            print(f"AIMessage: {content}\n")

    result = rag_chain({"question": user_question, "chat_history": chat_history})
    return result["answer"]
