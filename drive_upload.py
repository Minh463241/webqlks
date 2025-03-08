import os
import json
import base64
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Lấy biến môi trường
creds_b64 = os.environ.get("GDRIVE_CREDENTIALS")
if not creds_b64:
    raise Exception("Biến môi trường GDRIVE_CREDENTIALS chưa được thiết lập")

# Giải mã base64
creds_json = base64.b64decode(creds_b64).decode("utf-8")
creds_info = json.loads(creds_json)

# Tạo credentials
credentials = service_account.Credentials.from_service_account_info(creds_info, scopes=SCOPES)

FOLDER_ID = '121E26ll7oMi2rjZH4wTTjbntUd_4BOgH'

def upload_file_to_drive(file_path, filename):
    drive_service = build('drive', 'v3', credentials=credentials)

    file_metadata = {'name': filename}
    if FOLDER_ID:
        file_metadata['parents'] = [FOLDER_ID]

    media = MediaFileUpload(file_path, resumable=True)
    uploaded_file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()c

    file_id = uploaded_file.get('id')
    if not file_id:
        raise Exception("Không lấy được file_id từ response")

    # Tạo quyền truy cập công khai
    permission = {'type': 'anyone', 'role': 'reader'}
    drive_service.permissions().create(fileId=file_id, body=permission).execute()

    # Trả về URL xem trực tiếp
    direct_url = f"https://lh3.googleusercontent.com/d/{file_id}=w1000"
    return direct_url
