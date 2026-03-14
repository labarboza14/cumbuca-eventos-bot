import requests
import os

WEBHOOK = os.getenv("SLACK_WEBHOOK")

def send(msg):
    requests.post(WEBHOOK, json={"text": msg})

send("🚀 Bot da Cumbuca funcionando!")
