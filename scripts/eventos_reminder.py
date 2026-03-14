import requests
import re
from datetime import datetime, timedelta
import os

WEBHOOK_DM = os.getenv("SLACK_WEBHOOK")
WEBHOOK_CHANNEL = os.getenv("SLACK_WEBHOOK_CHANNEL")

urls = [
    "https://raw.githubusercontent.com/cumbucadev/comunidade/main/docs-temp/planejamento/2026.md",
    "https://raw.githubusercontent.com/cumbucadev/comunidade/main/docs-temp/nucleos/nucleo-eventos/docs/eventos-com-apoio-financeiro.md"
]

today = datetime.utcnow().date()

def send_dm(msg):
    if WEBHOOK_DM and WEBHOOK_DM.startswith("https://"):
        requests.post(WEBHOOK_DM, json={"text": msg})
    else:
        print("Webhook DM não configurado")

def send_channel(msg):
    if WEBHOOK_CHANNEL and WEBHOOK_CHANNEL.startswith("https://"):
        requests.post(WEBHOOK_CHANNEL, json={"text": msg})
    else:
        print("Webhook do canal não configurado")

events = []

for url in urls:

    text = requests.get(url).text
    lines = text.split("\n")

    for line in lines:

        # datas simples
        single = re.search(r"\b\d{2}/\d{2}\b", line)

        # datas com intervalo
        interval = re.search(r"\b(\d{2}/\d{2})\s*a\s*(\d{2}/\d{2})", line)

        if interval:
            start, end = interval.groups()
            date_str = end

        elif single:
            date_str = single.group()

        else:
            continue

        day, month = map(int, date_str.split("/"))

        try:
            event_date = datetime(today.year, month, day).date()
        except:
            continue

        events.append((event_date, line.strip()))

        # lembrete 1 dia antes
        if today == event_date - timedelta(days=1):

            send_dm(f"""
📢 Postar no LinkedIn amanhã

{line.strip()}
""")

# eventos da semana para o canal
week_events = []

for event_date, line in events:

    if today <= event_date <= today + timedelta(days=7):
        week_events.append(line)

if week_events:

    message = "📅 Agenda da semana — Cumbuca Dev\n\n"

    for e in week_events:
        message += f"• {e}\n"

    send_channel(message)
