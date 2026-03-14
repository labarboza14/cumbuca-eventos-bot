# Cumbuca Eventos Bot — Guia para Iniciantes (passo a passo)

Este repositório contém um bot que roda no **GitHub Actions** e envia mensagens no **Slack** com:

1. **Lembrete em DM (1 dia antes do evento):** “Postar no LinkedIn amanhã”
2. **Lista de eventos restantes do mês** em um canal

A ideia é que a comunidade mantenha as datas em um arquivo no repositório **cumbucadev/comunidade**, e o bot leia esse arquivo diariamente.

---

## 1) O que foi feito (em linguagem simples)

Antes, o bot tentava “adivinhar” as datas lendo documentos grandes e diferentes (planejamento e tabela de apoio financeiro). Isso é frágil, porque:

- existem datas que **não são eventos** (inscrições, deadlines, reuniões)
- as datas podem aparecer em **formatos diferentes** (ex.: inglês “April 7–8, 2026”)
- pode haver **mais de uma data na mesma linha**, e o bot pode pegar a errada

**Solução:** criar um arquivo “fonte oficial do bot” contendo **somente eventos**, com **1 evento por linha**, em formato fácil de ler pelo script.

---

## 2) Onde ficam os eventos (fonte oficial)

Os eventos que o bot lê ficam no repositório:

- **cumbucadev/comunidade**

Em um arquivo “limpo”, feito especialmente para o bot:

- `docs-temp/nucleos/nucleo-eventos/docs/eventos2026.md`

> Você pode manter os outros documentos (planejamento anual, tabela de apoio financeiro etc.).  
> Eles continuam úteis para humanos.  
> **Mas o bot usa este arquivo como fonte oficial**, porque ele é padronizado.

---

## 3) Como cadastrar um evento (modelo recomendado)

### Regras obrigatórias (para o bot funcionar)
- **1 evento por linha**
- a linha deve conter **uma data no formato `DD/MM`**
- evite colocar **outras datas na mesma linha** (tipo deadline), para não confundir o parser
- o bot assume o ano configurado no script (ex.: `YEAR = 2026`)

### Exemplo de conteúdo do arquivo `eventos2026.md`

```md
# Eventos 2026 — fonte do bot

## Regras
- 1 evento por linha
- sempre usar DD/MM
- não colocar deadlines/inscrições na mesma linha do evento

## Eventos
- 15/03 — [Planejamento] Encontro da Comunidade — https://link-do-evento
- 08/04 — [Apoio financeiro] PyTorch Conference Europe — https://events.linuxfoundation.org/pytorch-conference-europe/
- 18/05 — [Apoio financeiro] Open Source Summit North America — https://events.linuxfoundation.org/open-source-summit-north-america/
```

### Eventos de vários dias (importante)
O script atual entende intervalo assim: `09/03 a 20/03`  
**Mas ele considera a data do evento como sendo a data final do intervalo** (no exemplo, `20/03`).

Recomendação para iniciantes (mais previsível):
- se for um evento de vários dias e você quer o lembrete 1 dia antes do início, **coloque o dia inicial** como o “evento” (ou crie uma linha para cada dia).

Exemplo (evento de 2 dias):
- Opção simples (1 lembrete):
  - `07/04 — Conferência X (início) — link`

- Opção completa (1 lembrete antes de cada dia):
  - `07/04 — Conferência X (dia 1) — link`
  - `08/04 — Conferência X (dia 2) — link`

---

## 4) Como o bot decide “enviar DM 1 dia antes”

No script, a lógica é:

- ele lê todos os eventos e cria uma lista `events` com as datas encontradas
- para cada evento, ele verifica:

> se **hoje** for igual a (**data do evento** - 1 dia)  
> então envia uma DM: “Postar no LinkedIn amanhã”

Ou seja:
- Se hoje é **2026-03-14**, ele só envia DM se existir evento em **2026-03-15**.

### Atenção: o “hoje” é UTC
O script usa:

- `today = datetime.utcnow().date()`

Isso significa que o “dia” usado pode ser diferente do seu fuso local dependendo do horário.

---

## 5) Configuração do Slack (secrets)

O GitHub Actions passa 2 variáveis para o script:

- `SLACK_WEBHOOK` → webhook usado como “DM” (na prática, é um Incoming Webhook; depende de como você configurou no Slack)
- `SLACK_WEBHOOK_CHANNEL` → webhook do canal onde vai a lista “eventos restantes do mês”

Essas variáveis são configuradas como **Secrets** no repositório do bot (`labarboza14/cumbuca-eventos-bot`):

- `Settings` → `Secrets and variables` → `Actions` → `New repository secret`

Crie/atualize:
- `SLACK_WEBHOOK`
- `SLACK_WEBHOOK_CHANNEL`

---

## 6) Como o bot roda (GitHub Actions)

O workflow roda automaticamente todo dia via cron (UTC) e também pode ser rodado manualmente.

Para rodar manualmente:
1. Vá no repositório do bot: `labarboza14/cumbuca-eventos-bot`
2. Clique em **Actions**
3. Abra o workflow **Bot Cumbuca Eventos**
4. Clique em **Run workflow**

---

## 7) Como testar se está funcionando (passo a passo)

### Teste rápido do lembrete “amanhã tem evento”
1. No arquivo `eventos2026.md`, adicione um evento com data **amanhã** (em UTC).
   - Exemplo: se hoje (UTC) é `14/03`, coloque um evento `15/03`.
2. Rode o workflow manualmente no GitHub Actions.
3. Nos logs do Actions, você deve ver:
   - `Bot iniciado. Hoje: ...`
   - `Evento encontrado: ...`
4. Verifique no Slack se chegou a mensagem do lembrete.

### Se não chegou DM, as causas mais comuns são
- não existe nenhum evento com data “amanhã”
- o “hoje” em UTC não é o mesmo dia do seu relógio local
- `SLACK_WEBHOOK` não está configurado ou está apontando para outro lugar
- o Slack webhook falhou (o script hoje não imprime status code da resposta)

---

## 8) Boas práticas para evitar problemas

- Mantenha `eventos2026.md` como “arquivo limpo”: só eventos.
- Não misture deadlines/inscrições/reuniões no mesmo arquivo do bot.
- Garanta que cada linha de evento tenha exatamente **uma** data `DD/MM` (ou um intervalo, se você souber o efeito).
- Se o evento está em inglês (ex.: “April 7–8”), sempre adicione a versão `DD/MM` no arquivo do bot.

---

## 9) Dúvidas comuns

### “O bot não enviou DM, está com problema?”
Nem sempre. Ele só envia DM se houver evento “amanhã”.
Se amanhã não tem evento, não dispara nada para DM (comportamento esperado).

### “Ele manda DM de verdade?”
Ele usa `SLACK_WEBHOOK` (Incoming Webhook).
Dependendo de como o webhook foi criado no Slack, ele pode postar num canal ou numa conversa.
Se você precisa de DM real por usuário, aí é outro tipo de integração (Slack API + OAuth), não só webhook.

---

## 10) Checklist final (para iniciante)

- [ ] Criei/atualizei o arquivo `cumbucadev/comunidade/docs-temp/nucleos/nucleo-eventos/docs/eventos2026.md`
- [ ] Cada evento está em uma linha e tem `DD/MM`
- [ ] Atualizei o bot para ler o `raw.githubusercontent.com/.../eventos2026.md`
- [ ] Configurei os secrets `SLACK_WEBHOOK` e `SLACK_WEBHOOK_CHANNEL` no repo do bot
- [ ] Rodei o workflow manualmente e conferi os logs
- [ ] Cheguei mensagem no Slack (DM e/ou canal)

---
