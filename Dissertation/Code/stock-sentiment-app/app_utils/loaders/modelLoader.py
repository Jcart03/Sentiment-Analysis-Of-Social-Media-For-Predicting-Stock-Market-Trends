from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import os
import io
import zipfile

class ModelLoader:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
            return cls._instance
    def __init__(self, service_account_file:str, download_folder: str):
        if hasattr(self, '-initialized') and self._initialized:return
        self.service_account_file = service_account_file
        self.download_folder = download_folder
        self.zip_path = os.path.join(download_folder, "model_files.zip")
        self.creds = Credentials.from_service_account_file(
            self.service_account_file,
            scopes=['https://www.googleapis.com/auth/drive']
        )
        self.service = build('drive', 'v3', credentials=self.creds)
        self._initialized = True
        
    def download_and_extract(self, file_id:str, progress_callback=None):
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)
            
        if os.path.exists(self.zip_path):
            print("[ModelLoader] Model file already exists. Skipping download.")
            return
        request = self.service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh,request)
        print("[ModelLoader] Starting download...")
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"[ModelLoader] Download progress: {int(status.progress() * 100)}")
            if progress_callback:
                progress_callback(int(status.progress() * 100))
            
        
        
        with open(self.zip_path, 'wb') as f:
            f.write(fh.getbuffer())
        with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.download_folder)
            
    def get_model_path(self)-> str:
        return self.download_folder
    
        
        
            