import requests
import re
from datetime import datetime, timedelta
import os

WEBHOOK_DM = os.getenv("SLACK_WEBHOOK")
WEBHOOK_CHANNEL = os.getenv("SLACK_WEBHOOK_CHANNEL")

YEAR = 2026

URLS = [
    "https://raw.githubusercontent.com/cumbucadev/comunidade/main/docs-temp/planejamento/2026.md",
    "https://raw.githubusercontent.com/cumbucadev/comunidade/main/docs-temp/nucleos/nucleo-eventos/docs/eventos-com-apoio-financeiro.md",
]

today = datetime.utcnow().date()

print("Bot iniciado. Hoje:", today)

def send(webhook, msg):
    if webhook:
        try:
            requests.post(webhook, json={"text": msg})
        except Exception as e:
            print("Erro enviando Slack:", e)

events = []

for url in URLS:

    print("Lendo:", url)

    text = requests.get(url).text
    lines = text.split("\n")

    for line in lines:

        # intervalo 09/03 a 20/03
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
            event_date = datetime(YEAR, month, day).date()
        except:
            continue

        print("Evento encontrado:", event_date, line.strip())

        events.append((event_date, line.strip()))

# ---------------------------
# LEMBRETE LINKEDIN
# ---------------------------

for event_date, text in events:

    if today == event_date - timedelta(days=1):

        send(
            WEBHOOK_DM,
            f"📢 Postar no LinkedIn amanhã\n\n{text}"
        )

# ---------------------------
# EVENTOS RESTANTES DO MÊS
# ---------------------------

month_events = []

for event_date, text in events:

    if event_date.month == today.month and event_date >= today:
        month_events.append(text)

if month_events:

    message = "📅 Eventos restantes do mês — Cumbuca Dev\n\n"

    for e in month_events:
        message += f"• {e}\n"

    send(WEBHOOK_CHANNEL, message)

else:

    send(
        WEBHOOK_CHANNEL,
        "📅 Bot executado — nenhum evento restante neste mês."
    )


