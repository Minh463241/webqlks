import cloudinary
import cloudinary.uploader

# Cấu hình Cloudinary với thông tin trực tiếp
cloudinary.config(
    cloud_name="dwczro6hp",
    api_key="648677879979597",
    api_secret="-1D5fNq5hrtfGoIeZ8U7n8GHWi0",
    secure=True
)

def upload_file_to_cloudinary(file_path, filename, folder="rooms"):
    """
    Upload file lên Cloudinary và trả về URL của file.
    
    :param file_path: Đường dẫn file trên máy cục bộ.
    :param filename: Tên file sẽ được lưu trên Cloudinary (public_id).
    :param folder: Thư mục lưu trên Cloudinary.
    :return: secure_url của file đã upload.
    """
    upload_result = cloudinary.uploader.upload(file_path, folder=folder, public_id=filename)
    url = upload_result.get("secure_url")
    if not url:
        raise Exception("Không thể upload file lên Cloudinary.")
    return url
