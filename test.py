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
def send_discord_alert(confidence: int):
    if not DISCORD_WEBHOOK_URL:
        return False

    if confidence == 1:
        content = "📈 **Tín hiệu TĂNG** từ hệ thống AI!"
    elif confidence == 0:
        content = "📉 **Tín hiệu GIẢM** từ hệ thống AI!"
    else:
        return False  # Không gửi nếu không phải 0 hoặc 1

    message = {"content": content}
    response = requests.post(DISCORD_WEBHOOK_URL, json=message)
    return response.status_code == 204

@app.get("/ping")
async def ping():
    url = "https://api.nguyenchitrai.id.vn/confidence?limit=1"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

        latest = data.get("data", [])[0]
        confidence = latest.get("confidence")

        if confidence in [0, 1]:
            sent = send_discord_alert(confidence)
            return {
                "message": f"Alert sent to Discord. (confidence = {confidence})" if sent else "Failed to send alert."
            }
        else:
            return {"message": f"Không gửi alert. Confidence = {confidence}"}

    except Exception as e:
        return {"error": str(e)}

# uvicorn test:app --reload