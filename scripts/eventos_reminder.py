import requests
import re
from datetime import datetime, timedelta
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

def send(msg):
    requests.post(WEBHOOK, json={"text": msg})

for url in urls:

    text = requests.get(url).text
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

        events.append((event_date, line.strip()))

        # alerta 1 dia antes
        if today == event_date - timedelta(days=1):

            send(f"""
📢 Postar no LinkedIn amanhã

Evento:
{line.strip()}

Data: {date_str}
""")

# envio do resumo semanal (sábado)
if today.weekday() == 5:

    upcoming = []

    for event_date, line in events:

        if today <= event_date <= datetime(today.year, today.month, last_day).date():
            upcoming.append(line)

    if upcoming:

        message = "📅 Eventos restantes do mês\n\n"

        for e in upcoming:
            message += f"• {e}\n"

        message += "\n💡 Planeje os posts do LinkedIn."

        send(message)
