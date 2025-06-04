# DCNC Program and Course Advisor

An Anthropic Claude chatbot that can answer questions about RMIT programs and
courses using official program plans and course guides.

## Features

- Web chat interface using Streamlit chat
- AWS Bedrock backend using Cognito for authentication
- MariaDB database
- Contextual memory provided by LangChain [Messages](https://python.langchain.com/docs/concepts/messages/)
- Langchain [SQLDatabaseToolkit](https://python.langchain.com/api_reference/community/agent_toolkits/langchain_community.agent_toolkits.sql.toolkit.SQLDatabaseToolkit.html) and [zero-shot Agent](https://python.langchain.com/api_reference/langchain/agents/langchain.agents.agent.Agent.html)
- Dynamic system prompt features

### Programs

- 452 individual program plans
- Core courses list
- Major/minor list

### Courses

- 8334 course guides
- Course codes (if any)
- Course coordinator details
- Course prerequisites
- Course description

## Run It Yourself

You can run this chatbot locally with a [Python virtual environment](#run-with-python) or [Docker](#run-on-docker).

### 🐍 Run with Python

#### Clone the Repository

Open a terminal and go to the folder you want to clone the repository into, then run:

```bash
git clone https://www.github.com/misaka-12450/ask-dcnc.git
```

#### Add your Cognito Credentials

Rename the `.env.sample` file in the repository to `.env` and fill in the blanks.

#### Setup Virtual Environment and Install Dependencies

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

#### Run!

```bash
python streamlit run Chat.py
```

### 🚢 Run on Docker

[Install Docker](https://www.docker.com/get-started/)

#### Docker Run

Replace REPO_PATH with the path to the path you want to mount the repository to, and replace the environment variables with your own values.

```bash
docker run ghcr.io/misaka-12450/ask-dcnc:latest \
  -p 8501:8501 \
  -v REPO_PATH:/app \
  -e AWS_REGION='YOUR_AWS_REGION' \
  -e AWS_IDENTITY_POOL_ID='YOUR_AWS_IDENTITY_POOL_ID' \
  -e AWS_USER_POOL_ID='YOUR_AWS_USER_POOL_ID' \
  -e AWS_APP_CLIENT_ID='YOUR_AWS_APP_CLIENT_ID' \
  -e COGNITO_USERNAME='YOUR_COGNITO_USERNAME' \
  -e COGNITO_PASSWORD='YOUR_COGNITO_USERNAME' \
  -e MYSQL_HOST='YOUR_MYSQL_HOST' \
  -e MYSQL_PORT='YOUR_MYSQL_PORT' \
  -e MYSQL_DATABASE='YOUR_MYSQL_DATABASE' \
  -e MYSQL_USERNAME='YOUR_MYSQL_USERNAME' \
  -e MYSQL_PASSWORD='YOUR_MYSQL_PASSWORD'
```

You can access the app at:

```
http://YOUR_IP_ADDRESS:8501
```

#### Docker Compose with Cloudflare Tunnel

You can safely expose your app to the internet using a domain name without
messing with port forwarding by using
Cloudflare Tunnel.

Read
the [Cloudflare Tunnel documentation](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/get-started/create-remote-tunnel/)
on how to set up your tunnel and get the token:

> **Security Advice:** This application has not been thoroughly tested and is
> unsuitable for public access.
> In order to restrict access to your app, you should also hide your hostname
> behind [Cloudflare Zero Trust Access Policies](https://developers.cloudflare.com/cloudflare-one/applications/).

[Clone the repository](#clone-the-repository) and fill in the `.env` file with your values. Then run Docker Compose:

```bash
docker compose up -d
```


