# 🧠 Crypto Intelligence – Backend API & Notification

Đây là phần **Backend Web Service** của hệ thống **Crypto Intelligence**, phục vụ truy xuất dữ liệu giá, tín hiệu và dự đoán từ cơ sở dữ liệu, đồng thời gửi cảnh báo giao dịch đến Discord.

---

## 📌 Thành phần chính

### `app.py` – 📡 API Service

---

### `noti.py` – 🔔 Notification API

---

## 🧪 Công nghệ sử dụng

- **FastAPI** – framework API nhẹ, hiệu suất cao
- **Uvicorn** – ASGI server phục vụ API (kèm cấu hình [standard])
- **HTTPX / Requests** – Gửi HTTP request nội bộ hoặc webhook
- **python-dotenv** – Quản lý biến môi trường từ file `.env`
- **MongoDB (pymongo)** – Lưu trữ và truy xuất dữ liệu giá, tín hiệu và dự đoán

---

## ⚙️ Cài đặt & chạy local

### Yêu cầu:

- Python >= 3.10  
- Database đã được cập nhật dữ liệu bởi BE Worker
- Cấu hình `.env` hoặc `config.py` cho kết nối DB và webhook

### Các bước:

```bash
# 1. Clone project
git clone https://github.com/Nguyenchitrai62/BE_WEB_Crypto
cd BE_WEB_Crypto

# 2. Cài đặt thư viện
pip install -r requirements.txt

# 3. Chạy API chính (app.py)
uvicorn app:app --reload --port 8000

# 4. Chạy Notification API (noti.py)
uvicorn noti:app --reload --port 8001

## 🧩 Các thành phần khác của dự án
```

- ⚙️ **BE Worker – Xử lý tín hiệu & AI dự đoán (rule-based + LSTM)**  
  👉 [https://github.com/Nguyenchitrai62/BE_Worker](https://github.com/Nguyenchitrai62/BE_Worker)

- 🌐 **Frontend – Giao diện trực quan người dùng**  
  👉 [https://github.com/Nguyenchitrai62/FE_Crypto_Intelligence](https://github.com/Nguyenchitrai62/FE_Crypto_Intelligence)
