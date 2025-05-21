import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import asyncio

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
WEBHOOK_URL = os.getenv("WEBHOOK_URL") 

# Kết nối MongoDB Atlas
uri = f"mongodb+srv://trainguyenchi30:{MONGO_PASSWORD}@cryptodata.t2i1je2.mongodb.net/?retryWrites=true&w=majority&appName=CryptoData"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['my_database']
collection = db['chat_ids']

# Khởi tạo FastAPI app
app = FastAPI()

# Khởi tạo bot và application
bot = Bot(token=TELEGRAM_TOKEN)
application = Application.builder().token(TELEGRAM_TOKEN).build()

# Hàm xử lý lệnh /start
async def start(update: Update, context):
    chat_id = update.message.chat_id
    if not collection.find_one({"chat_id": chat_id}):
        collection.insert_one({"chat_id": chat_id})
        await update.message.reply_text(
            "🎉 Chào mừng bạn đến với bot dự đoán giá! 📈\n"
            "Bạn sẽ nhận thông báo ngay khi model AI của chúng tôi phát hiện giá tăng 📈 hoặc giảm 📉 với độ tin cậy cao! 🚀\n"
            "Hãy chờ tin từ chúng tôi nhé! 😊"
        )
    else:
        await update.message.reply_text(
            "🎉 Bạn đã đăng ký rồi! 📈\n"
            "Sẵn sàng nhận thông báo khi giá tăng 📈 hoặc giảm 📉 với độ tin cậy cao! 🚀"
        )

# Hàm gửi thông báo giá tăng
async def broadcast_price_increase():
    message = "⚠️ Cảnh báo: Model AI dự đoán giá sẽ tăng! 📈"
    cursor = collection.find({}, {"chat_id": 1})
    for doc in cursor:
        try:
            await bot.send_message(chat_id=doc["chat_id"], text=message)
        except Exception as e:
            print(f"Không thể gửi tin nhắn đến {doc['chat_id']}: {e}")

# Hàm giả lập kiểm tra dự đoán giá
def check_price_prediction():
    # Thay bằng logic gọi model AI
    return True  # Giả lập dự đoán giá tăng

# API endpoint để xử lý Webhook từ Telegram
@app.post("/webhook")
async def webhook(request: Request):
    update = Update.de_json(await request.json(), bot)
    if update:
        await application.process_update(update)
    return Response(status_code=200)

# API endpoint để gửi thông báo giá tăng (gọi từ model AI)
@app.post("/notify_price_increase")
async def notify_price_increase():
    if check_price_prediction():
        await broadcast_price_increase()
    return Response(status_code=200)

# Hàm khởi tạo khi FastAPI khởi động
@app.on_event("startup")
async def startup_event():
    try:
        # Kiểm tra kết nối MongoDB
        client.admin.command('ping')
        print("✅ Kết nối MongoDB thành công!")

        # Khởi tạo Telegram App
        await application.initialize()
        application.add_handler(CommandHandler("start", start))
        await application.start()

        # Thiết lập Webhook
        await application.bot.set_webhook(url=WEBHOOK_URL)
        print(f"✅ Webhook được thiết lập tại: {WEBHOOK_URL}")

    except Exception as e:
        print(f"❌ Lỗi khi khởi tạo bot: {e}")


# Hàm shutdown để đóng kết nối MongoDB
@app.on_event("shutdown")
async def shutdown_event():
    client.close()
    print("Đã đóng kết nối MongoDB")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8443)