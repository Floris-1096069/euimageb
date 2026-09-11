import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    #uploads
    UPLOAD_FOLDER = "static/uploads"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    #secret key
    SECRET_KEY = os.environ.get("SECRET_KEY", "secret")