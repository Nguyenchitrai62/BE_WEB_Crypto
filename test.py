import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler
from telegram import Bot
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# Load environment variables from .env file
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")

# Kết nối MongoDB Atlas
uri = f"mongodb+srv://trainguyenchi30:{MONGO_PASSWORD}@cryptodata.t2i1je2.mongodb.net/?retryWrites=true&w=majority&appName=CryptoData"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['my_database']
collection = db['chat_ids']

async def start(update, context):
    """Lưu chat_id vào MongoDB và gửi thông báo chào mừng với emoji."""
    chat_id = update.message.chat_id
    # Kiểm tra xem chat_id đã tồn tại chưa
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

async def broadcast_price_increase():
    """Gửi tin nhắn đến tất cả chat_id trong MongoDB khi giá được dự đoán tăng."""
    bot = Bot(token=TELEGRAM_TOKEN)
    message = "⚠️ Cảnh báo: Model AI dự đoán giá sẽ tăng! 📈"
    cursor = collection.find({}, {"chat_id": 1})
    for doc in cursor:
        try:
            await bot.send_message(chat_id=doc["chat_id"], text=message)
        except Exception as e:
            print(f"Không thể gửi tin nhắn đến {doc['chat_id']}: {e}")

def check_price_prediction():
    """Hàm giả lập kiểm tra dự đoán giá từ model AI."""
    # Thay bằng code gọi model AI của bạn
    # Ví dụ: model.predict() trả về True nếu giá tăng
    return True  # Giả lập dự đoán giá tăng

def main():
    """Chạy bot và kiểm tra dự đoán giá."""
    try:
        # Kiểm tra kết nối MongoDB
        client.admin.command('ping')
        print("Kết nối MongoDB thành công!")

        # Khởi tạo bot
        application = Application.builder().token(TELEGRAM_TOKEN).build()

        # Thêm handler cho lệnh /start
        application.add_handler(CommandHandler("start", start))

        # Bắt đầu bot
        application.run_polling()

        # Kiểm tra dự đoán giá (giả lập, thay bằng logic của bạn)
        if check_price_prediction():
            application.run_async(broadcast_price_increase())

    except Exception as e:
        print(f"Lỗi khi kết nối MongoDB hoặc chạy bot: {e}")
    finally:
        client.close()  # Đóng kết nối MongoDB khi bot dừng

if __name__ == "__main__":
    main()