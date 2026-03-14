import os
import re
import requests
from datetime import datetime, timedelta

WEBHOOK_DM = (os.getenv("SLACK_WEBHOOK") or "").strip()
WEBHOOK_CHANNEL = (os.getenv("SLACK_WEBHOOK_CHANNEL") or "").strip()

URLS = [
    "https://raw.githubusercontent.com/cumbucadev/comunidade/main/docs-temp/planejamento/2026.md",
    "https://raw.githubusercontent.com/cumbucadev/comunidade/main/docs-temp/nucleos/nucleo-eventos/docs/eventos-com-apoio-financeiro.md",
]

TIMEOUT_SECONDS = 20

today = datetime.utcnow().date()
YEAR = today.year

print("Executando bot - hoje (UTC):", today)

def valid_webhook(url: str) -> bool:
    # Validação simples e específica para Slack incoming webhooks
    return bool(url) and url.startswith("https://hooks.slack.com/services/")

def send(webhook: str, msg: str, label: str) -> bool:
    """
    Envia msg para um incoming webhook.
    Retorna True se enviou, False se não configurado/ inválido.
    Lança exception em falha de rede/HTTP.
    """
    if not valid_webhook(webhook):
        print(f"[{label}] webhook inválido ou não configurado")
        return False

    r = requests.post(webhook, json={"text": msg}, timeout=TIMEOUT_SECONDS)
    # Slack costuma retornar 200 + "ok"
    if r.status_code >= 400:
        raise RuntimeError(f"[{label}] Slack retornou HTTP {r.status_code}: {r.text[:200]}")
    print(f"[{label}] enviado com sucesso ({r.status_code})")
    return True

def download(url: str) -> str:
    r = requests.get(url, timeout=TIMEOUT_SECONDS)
    r.raise_for_status()
    return r.text

def parse_events(markdown_text: str):
    events = []
    for line in markdown_text.splitlines():
        interval = re.search(r"(\d{2}/\d{2})\s*a\s*(\d{2}/\d{2})", line)
        single = re.search(r"\b\d{2}/\d{2}\b", line)

        if interval:
            _, end = interval.groups()
            date_str = end
        elif single:
            date_str = single.group()
        else:
            continue

        try:
            day, month = map(int, date_str.split("/"))
            event_date = datetime(YEAR, month, day).date()
        except Exception:
            continue

        events.append((event_date, line.strip()))
    return events

# -------------------------
# COLETA EVENTOS
# -------------------------
events = []

for url in URLS:
    print("Lendo arquivo:", url)
    try:
        md = download(url)
    except Exception as e:
        print("Erro ao baixar arquivo:", repr(e))
        continue

    extracted = parse_events(md)
    for d, t in extracted:
        print("Evento detectado:", d, t)
    events.extend(extracted)

# -------------------------
# EVENTOS RESTANTES DO MÊS (CANAL + DM)
# -------------------------
month_events = [(d, t) for (d, t) in events if d.month == today.month and d >= today]
month_events.sort(key=lambda x: x[0])

if month_events:
    message = "📅 Eventos restantes do mês — Cumbuca Dev\n\n"
    for _, text in month_events:
        message += f"• {text}\n"

    try:
        # requisito 1: canal
        send(WEBHOOK_CHANNEL, message, "CANAL")

        # requisito 2: DM via webhook
        send(WEBHOOK_DM, message, "DM")
    except Exception as e:
        print("Erro enviando mensagem no Slack:", repr(e))
else:
    print("Nenhum evento restante neste mês")

# -------------------------
# LEMBRETE 1 DIA ANTES (DM)
# -------------------------
for event_date, text in events:
    if today == event_date - timedelta(days=1):
        reminder = f"📢 Amanhã tem evento\n\n{text}\n\nLembrete: postar no LinkedIn."
        try:
            send(WEBHOOK_DM, reminder, "DM-LEMBRETE")
        except Exception as e:
            print("Erro enviando DM de lembrete no Slack:", repr(e))
