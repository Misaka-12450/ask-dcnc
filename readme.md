# DCNC Program and Course Advisor

An Anthropic Claude chatbot that can answer questions about RMIT programs and
courses using official program plans and course guides.

## Features

- AWS Bedrock backend using Cognito for authentication
- MariaDB database
- Langchain chat history and SQL integration

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

You can run this chatbot locally with a Python virtual environment or Docker.

No matter which method you choose, you will need to first clone the repository
and fill in the `.env` file.

#### Clone the Repository

```bash
git clone https://www.github.com/misaka-12450/cosc1111-2502-a3
```

#### Add your Cognito Credentials

Rename the `.env.sample` file to `.env` and fill in the blanks.

### 🐍 Run with Python

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

```bash
docker run misaka12450/streamlit \
  -p 8501:8501 \
  -v REPO_PATH:/app \
  -e AWS_REGION='YOUR_AWS_REGION' \
  -e AWS_MODEL_ID='YOUR_AWS_MODEL_ID' \
  -e AWS_IDENTITY_POOL_ID='YOUR_AWS_IDENTITY_POOL_ID' \
  -e AWS_USER_POOL_ID='YOUR_AWS_USER_POOL_ID' \
  -e AWS_APP_CLIENT_ID='YOUR_AWS_APP_CLIENT_ID' \
  -e COGNITO_USERNAME='YOUR_COGNITO_USERNAME' \
  -e COGNITO_PASSWORD='YOUR_COGNITO_USERNAME'
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
>
behind [Cloudflare Zero Trust Access Policies](https://developers.cloudflare.com/cloudflare-one/applications/).

##### Docker Compose

Create a "docker-compose.yml" file in the same directory as the `.env` file with
the following content:

```
version: '3'
services:
  app:
    image: misaka12450/streamlit:latest

    environment:
      AWS_REGION: ${AWS_REGION}
      AWS_MODEL_ID: ${AWS_MODEL_ID}
      AWS_IDENTITY_POOL_ID: ${AWS_IDENTITY_POOL_ID}
      AWS_USER_POOL_ID: ${AWS_USER_POOL_ID}
      AWS_APP_CLIENT_ID: ${AWS_APP_CLIENT_ID}
      COGNITO_USERNAME: ${COGNITO_USERNAME}
      COGNITO_PASSWORD: ${COGNITO_PASSWORD}
    # volumes:
    #   - REPO_PATH:/app
    restart: always


  cloudflared:
    image: cloudflare/cloudflared
    command: tunnel --no-autoupdate run --token ${CLOUDFLARED_TOKEN}
    environment:
      CLOUDFLARED_TOKEN: ${CLOUDFLARED_TOKEN}
    restart: always
```

Run Docker Compose:

```bash
docker compose up -d
```


