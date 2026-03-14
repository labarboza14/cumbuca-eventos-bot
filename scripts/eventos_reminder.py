import requests
import re
from datetime import datetime, timedelta
import calendar
import os

WEBHOOK_DM = os.getenv("SLACK_WEBHOOK")
WEBHOOK_CHANNEL = os.getenv("SLACK_WEBHOOK_CHANNEL")

urls = [
    "https://raw.githubusercontent.com/cumbucadev/comunidade/main/docs-temp/planejamento/2026.md",
    "https://raw.githubusercontent.com/cumbucadev/comunidade/main/docs-temp/nucleos/nucleo-eventos/docs/eventos-com-apoio-financeiro.md"
]

today = datetime.utcnow().date()
last_day = calendar.monthrange(today.year, today.month)[1]

def send_dm(msg):
    if WEBHOOK_DM and WEBHOOK_DM.startswith("https://"):
        requests.post(WEBHOOK_DM, json={"text": msg})

def send_channel(msg):
    if WEBHOOK_CHANNEL and WEBHOOK_CHANNEL.startswith("https://"):
        requests.post(WEBHOOK_CHANNEL, json={"text": msg})

events = []

for url in urls:

    text = requests.get(url).text
    lines = text.split("\n")

    for line in lines:

        # datas simples
        single = re.search(r"\b\d{2}/\d{2}\b", line)

        # intervalos
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

Evento:
{line.strip()}
""")

# eventos restantes do mês para o canal
month_events = []

for event_date, line in events:

    if (
        event_date.month == today.month
        and today <= event_date <= datetime(today.year, today.month, last_day).date()
    ):
        month_events.append(line)

if month_events:

    message = "📅 Eventos restantes do mês — Cumbuca Dev\n\n"

    for e in month_events:
        message += f"• {e}\n"

    send_channel(message)
