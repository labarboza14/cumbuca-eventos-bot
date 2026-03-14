import requests
import os

WEBHOOK = os.getenv("SLACK_WEBHOOK")

requests.post(WEBHOOK, json={"text": "SCRIPT NOVO EXECUTANDO ✅"})
