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
    requests.post(WEBHOOK, json={"text": msg})

for url in urls:

    text = requests.get(url).text
    lines = text.split("\n")

    for line in lines:

        date_match = re.search(r"\d{2}/\d{2}/\d{4}", line)

        if date_match:

            date_str = date_match.group()
            event_date = datetime.strptime(date_str, "%d/%m/%Y").date()

            seven_days = event_date - timedelta(days=7)
            one_day = event_date - timedelta(days=1)

            if today == seven_days:

                send(f"""
✍️ Preparar post de evento

Data do evento: {date_str}

Informação encontrada no GitHub:
{line}
""")

            if today == one_day:

                send(f"""
📢 Postar evento amanhã

Data do evento: {date_str}

Informação encontrada no GitHub:
{line}
""")
