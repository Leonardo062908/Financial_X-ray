import os
import json
import requests
from fastapi import APIRouter, Request, Query
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

router = APIRouter()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "")
GRAPH_API_VERSION = os.getenv("GRAPH_API_VERSION", "v20.0")

@router.get("/webhook")
def verify_webhook(
    hub_mode: Optional[str] = Query(default=None, alias="hub.mode"),
    hub_challenge: Optional[str] = Query(default=None, alias="hub.challenge"),
    hub_verify_token: Optional[str] = Query(default=None, alias="hub.verify_token"),
):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN and hub_challenge:
        return PlainTextResponse(content=hub_challenge, status_code=200)

    return PlainTextResponse(content="Verification Failed", status_code=403)

@router.post("/webhook")
async def receive_webhook(request: Request):
    body = await request.json()

    print("=== INCOMING WEBHOOK ===")
    print(json.dumps(body, indent=2, ensure_ascii=False))

    try:
        await try_auto_reply(body)
    except Exception as e:
        print("AUTO_REPLY_ERROR:", str(e))

    return {"status": "ok"}

async def try_auto_reply(body: dict):
    """
    Extrai a mensagem e responde automaticamente.
    Sendo esse o 'echo bot' básico.
    """
    entry = body.get("entry", [])
    if not entry:
        return

    changes = entry[0].get("changes", [])
    if not changes:
        return

    value = changes[0].get("value", {})
    messages = value.get("messages", [])
    if not messages:
        return

    msg = messages[0]
    from_number = msg.get("from") #Telefone do usuário que enviou a mensagem
    msg_body = msg.get("type")

    #Apenas respondendo a mensagens de texto
    if msg_body != "text":
        text = "Recebi seu arquivo!✅ Já vou analisar e te retorno em breve.⏳"
    else:
        text = "Recebi ✅ Me envie sua fatura (PDF ou imagem) e em 1 frase sua maior dor financeira no momento."
    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": from_number,
        "type": "text",
        "text": {
            "body": text
        },
    }

    r = requests.post(url, headers=headers, json=payload, timeout=20)
    print("SEND STATUS:", r.status_code, r.text)
    r.raise_for_status()