# Integration pipelines with Python SDK

## Install dependencies

```shell
pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Environment

Before start we have to create `.env` file, from `.env.tpl`.
Environment has to contain three variables for SDK access to Aidbox: `AIDBOX_URL`, `AIDBOX_CLIENT_USERNAME` and `AIDBOX_CLIENT_PASSWORD` (username and password from aidbox basic client). And `AIDBOX_LICENSE` which is possible
to obtain on portal.

## Run Aidbox in Docker

```shell
docker compose up
```

## Run python server

```shell
python server.py
```
