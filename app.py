import os
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pymongo import MongoClient, DESCENDING
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from datetime import datetime

# Load biến môi trường từ .env
load_dotenv()
password = os.getenv("MONGO_PASSWORD")

# Kết nối MongoDB Atlas
uri = f"mongodb+srv://trainguyenchi30:{password}@cryptodata.t2i1je2.mongodb.net/?retryWrites=true&w=majority&appName=CryptoData"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['my_database']
collection = db['my_collection']

# Tạo FastAPI app
app = FastAPI()

# API để lấy kết nối WebSocket
@app.get("/latest-confidence")
async def latest_confidence():
    return {"message": "Connect to WebSocket to receive confidence updates every 5 seconds."}

# WebSocket route
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # Chấp nhận kết nối WebSocket
    
    try:
        while True:
            # Lấy dữ liệu từ MongoDB (Document với Date mới nhất)
            latest_doc = collection.find_one(
                {}, sort=[('Date', DESCENDING)],
                projection={'_id': 0, 'Date': 1, 'confidence': 1}
            )
            
            if latest_doc:
                # Gửi dữ liệu mới nhất qua WebSocket
                message = {
                    'date': str(latest_doc['Date']),
                    'confidence': latest_doc['confidence']
                }
                await websocket.send_json(message)  # Gửi dữ liệu
            else:
                # Nếu không có dữ liệu, gửi lỗi
                await websocket.send_json({'error': 'No data found'})
            
            # Gửi dữ liệu mỗi 3 giây
            await asyncio.sleep(1)
    
    except WebSocketDisconnect:
        print("Client disconnected")

# Để chạy ứng dụng FastAPI, dùng `uvicorn`
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
# uvicorn app:app --reload
