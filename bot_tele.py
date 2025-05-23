import os
import asyncio
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler
from telegram import Bot
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from fastapi import FastAPI
import uvicorn
from threading import Thread

# Load biến môi trường
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")

# Khởi tạo MongoDB
uri = f"mongodb+srv://trainguyenchi30:{MONGO_PASSWORD}@cryptodata.t2i1je2.mongodb.net/?retryWrites=true&w=majority&appName=CryptoData"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['my_database']
chat_collection = db['chat_ids']
AI_collection = db['my_collection']

# Khởi tạo FastAPI và Telegram Bot
app = FastAPI()
bot = Bot(token=TELEGRAM_TOKEN)

# Hàm gửi tin nhắn cho tất cả user
async def send_alert_to_all_users(message: str):
    cursor = chat_collection.find({}, {"chat_id": 1})
    for doc in cursor:
        try:
            await bot.send_message(chat_id=doc["chat_id"], text=message)
        except Exception as e:
            print(f"❌ Không thể gửi tin nhắn đến {doc['chat_id']}: {e}")

@app.get("/ping")
async def ping():
    try:
        confidence = AI_collection.find_one({}, sort=[("Date", -1)])["confidence"]

        if confidence > 0.9:
            message = f"💥 Đáy lắm rồi đó, gom lẹ không kịp! (confidence: {confidence:.2f})"
            await send_alert_to_all_users(message)

        elif confidence > 0.8:
            message = f"🛒 Có vẻ giá đang ở vùng hấp dẫn đấy... (confidence: {confidence:.2f})"
            await send_alert_to_all_users(message)

        elif confidence > 0.7:
            message = f"📈 Giá sắp tăng rồi đó nhen! (confidence: {confidence:.2f})"
            await send_alert_to_all_users(message)

        elif confidence < 0.1:
            message = f"🔺 Đỉnh lắm rồi, chốt lời chưa bạn ơi! (confidence: {confidence:.2f})"
            await send_alert_to_all_users(message)

        elif confidence < 0.2:
            message = f"📉 Giá cao rồi, coi chừng đu đỉnh... (confidence: {confidence:.2f})"
            await send_alert_to_all_users(message)

        elif confidence < 0.3:
            message = f"🤔 Có dấu hiệu đỉnh đó, cẩn thận nha! (confidence: {confidence:.2f})"
            await send_alert_to_all_users(message)

    except Exception as e:
        print(f"❌ Lỗi trong /ping: {e}")

    # Ping trả về message vui tính để giữ cho app Render không bị sleep
    return {"message": "🧠 Tao vẫn còn thở, đừng lo! Hệ hệ hệ..."}

# Lệnh /start lưu chat_id
async def start(update, context):
    chat_id = update.message.chat_id
    if not chat_collection.find_one({"chat_id": chat_id}):
        chat_collection.insert_one({"chat_id": chat_id})
        await update.message.reply_text(
            "✨ Chào mừng bạn đến với BOT phân tích tâm linh học thuật! 📊🔮\n"
            "Từ nay bạn sẽ được AI thì thầm mỗi khi thị trường có biến động bất thường... 😎📈📉\n"
            "Chỉ cần giữ bình tĩnh, bật thông báo và... đợi tín hiệu vũ trụ gửi về nhé! 🚀🧘‍♂️"
        )
    else:
        await update.message.reply_text(
            "👀 Bạn đăng ký rồi mà! Đang nằm vùng chờ tín hiệu đúng không? 🔔📲\n"
            "Yên tâm, khi có biến là bot hú liền không chậm một nhịp! 😤📡"
        )

# Chạy Telegram bot
async def run_telegram_bot():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    await asyncio.Event().wait()

# Chạy FastAPI server
def run_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

# Hàm chính chạy cả Telegram và FastAPI song song
def main():
    try:
        client.admin.command('ping')
        print("✅ Kết nối MongoDB thành công!")

        fastapi_thread = Thread(target=run_fastapi)
        fastapi_thread.daemon = True
        fastapi_thread.start()

        asyncio.run(run_telegram_bot())

    except Exception as e:
        print(f"❌ Lỗi khi chạy hệ thống: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    main()
