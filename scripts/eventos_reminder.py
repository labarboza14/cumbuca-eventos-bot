import requests
import re
from datetime import datetime, timedelta
import os

WEBHOOK = os.getenv("SLACK_WEBHOOK")

urls = [
    "https://raw.githubusercontent.com/cumbucadev/comunidade/main/docs-temp/planejamento/2026.md",
    "https://raw.githubusercontent.com/cumbucadev/comunidade/main/docs-temp/nucleos/nucleo-eventos/docs/eventos-com-apoio-financeiro.md"
]

today = datetime.utcnow().date()

def send(msg):
    print("Enviando mensagem para Slack...")
    requests.post(WEBHOOK, json={"text": msg})

seen = set()

for url in urls:

    print(f"Lendo arquivo: {url}")

    response = requests.get(url)
    text = response.text
    lines = text.split("\n")

    for line in lines:

        date_match = re.search(r"\b\d{2}/\d{2}\b", line)

        if not date_match:
            continue

        date_str = date_match.group()

        if date_str in seen:
            continue

        seen.add(date_str)

        day, month = map(int, date_str.split("/"))

        try:
            event_date = datetime(today.year, month, day).date()
        except:
            continue

        seven_days = event_date - timedelta(days=7)
        one_day = event_date - timedelta(days=1)

        if today == seven_days:

            send(f"""
✍️ Preparar post de evento

Data do evento: {date_str}

Contexto encontrado:
{line.strip()}
""")

        if today == one_day:

            send(f"""
📢 Postar evento amanhã

Data do evento: {date_str}

Contexto encontrado:
{line.strip()}
""")
