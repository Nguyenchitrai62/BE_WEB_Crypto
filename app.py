import os
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import JSONResponse
from pymongo import MongoClient, DESCENDING
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # Cho phép mọi domain gọi API
    allow_credentials=True,
    allow_methods=["*"],    # Cho phép mọi phương thức GET, POST,...
    allow_headers=["*"],    # Cho phép mọi headers
)

# Endpoint test server
@app.get("/ping")
async def ping():
    return {"message": "Server alive"}

# WebSocket stream dữ liệu mới nhất
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            latest_doc = collection.find_one(
                {},
                sort=[('Date', DESCENDING)],
                projection={'_id': 0, 'Date': 1, 'confidence': 1}
            )

            if latest_doc:
                message = {
                    'date': str(latest_doc['Date']),
                    'confidence': latest_doc['confidence']
                }
                await websocket.send_json(message)
            else:
                await websocket.send_json({'error': 'No data found'})

            await asyncio.sleep(1)

    except WebSocketDisconnect:
        print("Client disconnected")

# API để lấy 100 confidence gần nhất
@app.get("/confidence")
async def get_recent_confidence(limit: int = Query(100, ge=1, le=1000)):
    """
    Lấy 'limit' confidence gần nhất. Mặc định là 100, tối đa 1000.
    Bao gồm cả giá close.
    """
    try:
        recent_docs = list(collection.find(
            {},
            sort=[('Date', DESCENDING)],
            projection={'_id': 0, 'Date': 1, 'confidence': 1, 'Close': 1}  # Thêm close
        ).limit(limit))

        for doc in recent_docs:
            doc['Date'] = str(doc['Date'])

        return JSONResponse(content={"data": recent_docs})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# Để chạy ứng dụng FastAPI
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Chạy server với:
# uvicorn app:app --reload
