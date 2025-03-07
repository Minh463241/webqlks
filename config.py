import os
from dotenv import load_dotenv

# Tải biến môi trường từ file .env nếu có
load_dotenv()

# Lấy các biến môi trường cần thiết
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

# Kiểm tra và thông báo lỗi nếu biến môi trường chưa được thiết lập
if not MONGO_URI:
    raise Exception("MONGO_URI chưa được thiết lập trong biến môi trường")
if not DB_NAME:
    raise Exception("DB_NAME chưa được thiết lập trong biến môi trường")
