from fastapi import FastAPI, WebSocket
from typing import List
import requests
from config.config_loader import CONFIG
import asyncio

app = FastAPI()

# Lista de conexões WebSocket ativas
active_connections: List[WebSocket] = []

@app.websocket("/ws/notifications")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await asyncio.sleep(1)  # Mantém a conexão aberta
    except Exception:
        pass
    finally:
        active_connections.remove(websocket)

async def send_notification(message: str):
    for connection in active_connections:
        await connection.send_text(message)

# --- Integração com Telegram ---
TELEGRAM_BOT_TOKEN = CONFIG['services']['notification']['provider'] == 'email' and CONFIG['services']['notification'].get('telegram_bot_token', '') or ''
TELEGRAM_CHAT_ID = CONFIG['services']['notification'].get('telegram_chat_id', '')

def send_telegram_notification(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, data=data)

# --- Integração com WhatsApp (usando API externa como UltraMsg, Z-API, etc) ---
WHATSAPP_API_URL = CONFIG['services']['notification'].get('whatsapp_api_url', '')
WHATSAPP_TOKEN = CONFIG['services']['notification'].get('whatsapp_token', '')
WHATSAPP_PHONE = CONFIG['services']['notification'].get('whatsapp_phone', '')

def send_whatsapp_notification(message: str):
    # Exemplo para UltraMsg
    url = f"{WHATSAPP_API_URL}/messages/chat"
    data = {"token": WHATSAPP_TOKEN, "to": WHATSAPP_PHONE, "body": message}
    requests.post(url, data=data)

# --- Função unificada ---
def notify_all(message: str):
    import asyncio
    asyncio.create_task(send_notification(message))
    send_telegram_notification(message)
    send_whatsapp_notification(message)
