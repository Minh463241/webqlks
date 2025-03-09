import os
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

# ---------------------------
# Cấu hình MongoDB trực tiếp
# ---------------------------
MONGO_URI = "mongodb+srv://minh:123@cluster0.wcrhx.mongodb.net/qlksda?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "qlksda"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# ---------------------------
# (Chú ý) Cấu hình Cloudinary (dùng trực tiếp nếu cần)
# ---------------------------
# CLOUDINARY_CLOUD_NAME = "dwczro6hp"
# CLOUDINARY_API_KEY = "648677879979597"
# CLOUDINARY_API_SECRET = "-1D5fNq5hrtfGoIeZ8U7n8GHWi0"
CLOUDINARY_URL="cloudinary://648677879979597:-1D5fNq5hrtfGoIeZ8U7n8GHWi0@dwczro6hp"

# ---------------------------
# Các collection
# ---------------------------
customers_collection        = db['customers']
room_images_collection      = db['room_images']
bookings_collection         = db['bookings']
services_collection         = db['services']
invoices_collection         = db['invoices']
invoice_services_collection = db['invoice_services']
room_types_collection       = db['room_types']
staff_collection            = db['staff']
rooms_collection            = db['rooms']

# ---------------------------
# Khách hàng
# ---------------------------
def get_customer_by_email(email):
    return customers_collection.find_one({'Email': email})

def create_customer(customer_data):
    result = customers_collection.insert_one(customer_data)
    return str(result.inserted_id)

def update_last_login(email):
    result = customers_collection.update_one(
        {'Email': email},
        {'$set': {'last_login': datetime.utcnow()}}
    )
    return result.modified_count

def update_user_avatar(email, avatar_filename):
    result = customers_collection.update_one(
        {'Email': email},
        {'$set': {'avatar': avatar_filename}}
    )
    return result.modified_count

def update_customer(email, update_data):
    """
    Cập nhật thông tin khách hàng dựa trên email.
    update_data có thể chứa các trường:
      - "HoTen": Tên khách hàng
      - "DienThoai": Số điện thoại
      - "CMND": CCCD/Hộ chiếu
      - "DiaChi": Địa chỉ
      - "avatar": Tên file avatar mới
      - "bg_image": Tên file ảnh nền giao diện mới
      - "password": Mật khẩu mới (nên mã hóa trước khi lưu)
    """
    result = customers_collection.update_one(
        {"Email": email},
        {"$set": update_data}
    )
    return result.modified_count

# ---------------------------
# Ảnh phòng
# ---------------------------
def create_room_image(room_image_data):
    result = room_images_collection.insert_one(room_image_data)
    return str(result.inserted_id)

def get_room_images_by_room(ma_phong):
    return list(room_images_collection.find({'MaPhong': ma_phong}))

# ---------------------------
# Đặt phòng
# ---------------------------
def create_booking(booking_data):
    result = bookings_collection.insert_one(booking_data)
    return str(result.inserted_id)

def get_booking_by_id(ma_dat_phong):
    return bookings_collection.find_one({'MaDatPhong': ma_dat_phong})

def update_booking(ma_dat_phong, update_data):
    result = bookings_collection.update_one(
        {'MaDatPhong': ma_dat_phong},
        {'$set': update_data}
    )
    return result.modified_count

def is_room_booked(ma_phong, checkin_date, checkout_date):
    booking = bookings_collection.find_one({
        'MaPhong': ma_phong,
        'NgayNhan': {'$lt': checkout_date},
        'NgayTra': {'$gt': checkin_date}
    })
    return booking is not None

# ---------------------------
# Dịch vụ
# ---------------------------
def get_service_by_id(ma_dich_vu):
    return services_collection.find_one({'MaDichVu': ma_dich_vu})

def create_service(service_data):
    result = services_collection.insert_one(service_data)
    return str(result.inserted_id)

def get_all_services():
    return list(services_collection.find())

# ---------------------------
# Hóa đơn
# ---------------------------
def create_invoice(invoice_data):
    result = invoices_collection.insert_one(invoice_data)
    return str(result.inserted_id)

def get_invoice_by_id(ma_hoa_don):
    return invoices_collection.find_one({'MaHoaDon': ma_hoa_don})

def get_all_invoices():
    return list(invoices_collection.find())

# ---------------------------
# Hóa đơn dịch vụ
# ---------------------------
def create_invoice_service(invoice_service_data):
    result = invoice_services_collection.insert_one(invoice_service_data)
    return str(result.inserted_id)

def get_invoice_services_by_invoice(ma_hoa_don):
    return list(invoice_services_collection.find({'MaHoaDon': ma_hoa_don}))

# ---------------------------
# Loại phòng
# ---------------------------
def get_all_room_types():
    return list(room_types_collection.find())

def get_room_type_by_id(ma_loai_phong):
    return room_types_collection.find_one({'MaLoaiPhong': ma_loai_phong})

def create_room_type(room_type_data):
    result = room_types_collection.insert_one(room_type_data)
    return str(result.inserted_id)

# Alias để dùng trong app
add_room_type = create_room_type

def add_room_to_db(so_phong, ma_loai_phong, mo_ta, trang_thai):
    try:
        room_type = room_types_collection.find_one({'_id': ObjectId(ma_loai_phong)})
    except Exception as e:
        raise ValueError("ID loại phòng không hợp lệ: " + str(ma_loai_phong))
    if not room_type:
        raise ValueError("Không tìm thấy loại phòng với ID: " + str(ma_loai_phong))
    
    price = room_type.get('price', 0)
    room_data = {
        'MaPhong': None,  # Sẽ được cập nhật sau khi chèn
        'SoPhong': so_phong,
        'MaLoaiPhong': ma_loai_phong,  # Lưu ID loại phòng dưới dạng string
        'TrangThai': trang_thai,
        'MoTa': mo_ta,
        'price': price,
        'created_at': datetime.utcnow()
    }
    return create_room(room_data)

def add_room_with_image(file_path, filename, so_phong, ma_loai_phong, mo_ta, image_description="", trang_thai="Trống"):
    # Tạo phòng mới và lấy ID phòng
    room_id = add_room_to_db(so_phong, ma_loai_phong, mo_ta, trang_thai)
    
    # Sử dụng hàm upload từ file drive_upload.py để tải ảnh lên (giả sử hàm trả về URL ảnh)
    from drive_upload import upload_file_to_drive
    image_url = upload_file_to_drive(file_path, filename)

    room_image_data = {
        'MaAnh': None,
        'MaPhong': room_id,         # Liên kết ảnh với phòng vừa tạo
        'DuongDanAnh': image_url,   # Đường dẫn ảnh từ Google Drive (hoặc Cloud)
        'MoTa': image_description,
        'uploaded_at': datetime.utcnow()
    }
    create_room_image(room_image_data)
    
    # Cập nhật document phòng với thông tin ảnh để hiển thị trong danh sách phòng
    update_room(room_id, {'image_url': image_url, 'image_url_hd': image_url})
    
    return room_id

# ---------------------------
# Nhân viên (Admin)
# ---------------------------
def get_staff_by_email(email):
    return staff_collection.find_one({'Email': email})

def create_staff(staff_data):
    """
    Tạo một tài khoản nhân viên mới.
    Nếu không có trường 'role' trong staff_data, mặc định gán là 'staff'.
    Lưu ý: Nên mã hóa mật khẩu trước khi lưu.
    """
    if 'role' not in staff_data or not staff_data['role']:
        staff_data['role'] = 'staff'
    staff_data['created_at'] = datetime.utcnow()
    result = staff_collection.insert_one(staff_data)
    return str(result.inserted_id)

def get_all_staff():
    """
    Lấy danh sách tất cả nhân viên, bao gồm các trường cần thiết như tên, email và role.
    """
    staff_list = list(staff_collection.find({}, {"HoTen": 1, "Email": 1, "role": 1}))
    return staff_list

def update_staff_role(staff_id, new_role):
    """
    Cập nhật vai trò (role) của nhân viên.
    Chỉ chấp nhận các giá trị role hợp lệ: 'admin' hoặc 'staff'.
    """
    if new_role not in ['admin', 'staff']:
        raise ValueError("Vai trò không hợp lệ")
    result = staff_collection.update_one(
        {"_id": ObjectId(staff_id)},
        {"$set": {"role": new_role}}
    )
    return result.modified_count

def get_staff_by_id(staff_id):
    """
    Lấy thông tin của 1 nhân viên theo _id.
    """
    return staff_collection.find_one({"_id": ObjectId(staff_id)})

def update_staff_info(staff_id, update_data):
    """
    Cập nhật thông tin của nhân viên dựa trên staff_id.
    update_data là một dictionary chứa các trường cần cập nhật.
    """
    result = staff_collection.update_one(
        {"_id": ObjectId(staff_id)},
        {"$set": update_data}
    )
    return result.modified_count

def delete_staff(staff_id):
    """
    Xóa tài khoản nhân viên khỏi collection.
    """
    result = staff_collection.delete_one({"_id": ObjectId(staff_id)})
    return result.deleted_count

# ---------------------------
# Các hàm lấy dữ liệu về trang cá nhân (lịch sử đặt phòng, dịch vụ sử dụng)
# ---------------------------
def get_booking_history_by_customer(email):
    """
    Lấy danh sách booking (đặt phòng) của khách hàng dựa trên email.
    """
    return list(bookings_collection.find({"email": email}))

def get_services_used_by_customer(email):
    """
    Lấy danh sách dịch vụ đã sử dụng của khách hàng dựa trên email.
    """
    # Tìm hóa đơn của khách hàng
    invoices = list(invoices_collection.find({"email": email}))
    services_used = []
    for invoice in invoices:
        invoice_id = invoice.get('MaHoaDon')
        if not invoice_id:
            continue
        invoice_services = list(invoice_services_collection.find({"MaHoaDon": invoice_id}))
        for inv_service in invoice_services:
            service = services_collection.find_one({"MaDichVu": inv_service.get("MaDichVu")})
            if service:
                services_used.append(service)
            else:
                services_used.append(inv_service)
    return services_used
