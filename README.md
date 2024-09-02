# Elecdis_CSMS_OCPP_1.6-BackEnd

# Backend Project

## Description

This is a FastAPI backend project Elecdis_CSMS.

## Setup

1. Create and activate a virtual environment:

```sh
python3 -m venv venv
source venv/bin/activate # On Windows use `venv\Scripts\activate`
$ cp .env.backend .env
pip install -r requirements.txt

```

2. Using command docker compose

```sh
docker compose build
docker-compose up -d

```

3. Configuration .env

```sh
DATABASE_URL=postgresql://elecdis:elecdis-ocpp@{votre_host}:5432/elecdis


```
