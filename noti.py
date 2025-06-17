from fastapi import FastAPI
import httpx
import requests
from dotenv import load_dotenv
import os

# Load biến môi trường từ .env
load_dotenv()

app = FastAPI()

# Lấy webhook từ biến môi trường
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# Gửi cảnh báo đến Discord
def send_discord_alert(symbol: str, confidence: int):
    if not DISCORD_WEBHOOK_URL:
        return False

    if confidence == 1:
        content = f"📈 **Tín hiệu TĂNG** cho {symbol} từ hệ thống AI!"
    elif confidence == 0:
        content = f"📉 **Tín hiệu GIẢM** cho {symbol} từ hệ thống AI!"
    else:
        return False  # Không gửi nếu không phải 0 hoặc 1

    message = {"content": content}
    response = requests.post(DISCORD_WEBHOOK_URL, json=message)
    return response.status_code == 204

@app.get("/ping")
async def ping():
    base_url = "https://api.nguyenchitrai.id.vn/confidence?limit=1&symbol="
    symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT"]
    results = {}

    try:
        async with httpx.AsyncClient() as client:
            for symbol in symbols:
                url = base_url + symbol
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()

                latest = data.get("data", [])[0]
                confidence = latest.get("confidence")

                if confidence in [0, 1]:
                    sent = send_discord_alert(symbol, confidence)
                    results[symbol] = f"Sent alert (confidence = {confidence})" if sent else "Failed to send alert"
                else:
                    results[symbol] = f"Không gửi alert. Confidence = {confidence}"

        return results

    except Exception as e:
        return {"error": str(e)}

# uvicorn test:app --reload