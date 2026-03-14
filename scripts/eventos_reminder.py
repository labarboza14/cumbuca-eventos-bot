import requests
import re
from datetime import datetime, timedelta
import os

WEBHOOK_DM = os.getenv("SLACK_WEBHOOK")
WEBHOOK_CHANNEL = os.getenv("SLACK_WEBHOOK_CHANNEL")

URLS = [
    "https://raw.githubusercontent.com/cumbucadev/comunidade/main/docs-temp/planejamento/2026.md",
    "https://raw.githubusercontent.com/cumbucadev/comunidade/main/docs-temp/nucleos/nucleo-eventos/docs/eventos-com-apoio-financeiro.md",
]

today = datetime.utcnow().date()
year = today.year

print("Hoje:", today)

def send_dm(message):
    if WEBHOOK_DM:
        requests.post(WEBHOOK_DM, json={"text": message})

def send_channel(message):
    if WEBHOOK_CHANNEL:
        requests.post(WEBHOOK_CHANNEL, json={"text": message})

events = []

for url in URLS:

    print("Lendo:", url)

    text = requests.get(url).text
    lines = text.split("\n")

    for line in lines:

        # captura intervalo de datas
        interval = re.search(r"(\d{2}/\d{2})\s*a\s*(\d{2}/\d{2})", line)

        if interval:
            start, end = interval.groups()
            date_str = end

        else:

            single = re.search(r"\b\d{2}/\d{2}\b", line)

            if not single:
                continue

            date_str = single.group()

        day, month = map(int, date_str.split("/"))

        try:
            event_date = datetime(year, month, day).date()
        except:
            continue

        print("Evento detectado:", event_date, line.strip())

        events.append((event_date, line.strip()))

# -----------------------
# LEMBRETE 1 DIA ANTES
# -----------------------

for event_date, text in events:

    if today == event_date - timedelta(days=1):

        send_dm(
            f"""
📢 Postar no LinkedIn amanhã

{text}
"""
        )

# -----------------------
# EVENTOS RESTANTES DO MÊS
# -----------------------

month_events = []

for event_date, text in events:

    if event_date.month == today.month and event_date >= today:
        month_events.append((event_date, text))

month_events.sort()

if month_events:

    message = "📅 Eventos restantes do mês — Cumbuca Dev\n\n"

    for date, text in month_events:
        message += f"• {text}\n"

    send_channel(message)

else:

    print("Nenhum evento restante no mês")
