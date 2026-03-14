import requests
import re
from datetime import datetime
import calendar
import os

WEBHOOK = os.getenv("SLACK_WEBHOOK")

urls = [
    "https://raw.githubusercontent.com/cumbucadev/comunidade/main/docs-temp/planejamento/2026.md",
    "https://raw.githubusercontent.com/cumbucadev/comunidade/main/docs-temp/nucleos/nucleo-eventos/docs/eventos-com-apoio-financeiro.md"
]

today = datetime.utcnow().date()

last_day = calendar.monthrange(today.year, today.month)[1]

events = []

for url in urls:

    response = requests.get(url)
    text = response.text
    lines = text.split("\n")

    for line in lines:

        match = re.search(r"\b\d{2}/\d{2}\b", line)

        if not match:
            continue

        date_str = match.group()

        day, month = map(int, date_str.split("/"))

        if month != today.month:
            continue

        event_date = datetime(today.year, month, day).date()

        if today <= event_date <= datetime(today.year, month, last_day).date():

            events.append(f"{date_str} — {line.strip()}")

if events:

    message = "📅 Eventos restantes do mês\n\n"

    for e in events:
        message += f"• {e}\n"

    message += "\n💡 Planeje os posts do LinkedIn com antecedência."

    requests.post(WEBHOOK, json={"text": message})
