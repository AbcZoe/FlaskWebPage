import os  # 匯入操作系統模組，用於讀取環境變數

class Config:
    # 設定應用程式的密鑰，用於安全功能，例如 session 保護
    SECRET_KEY = 'eb5480089fb042e12832c2c09c9b22b9'
    # 設定資料庫 URI，這裡使用 SQLite，資料庫檔案名為 site.db
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    # 設定郵件伺服器資訊
    MAIL_SERVER = 'smtp.googlemail.com'  # 郵件伺服器地址
    MAIL_PORT = 587  # 郵件伺服器端口
    MAIL_USE_TLS = True  # 使用 TLS 加密
    MAIL_USERNAME = os.environ.get('EMAIL_USER')  # 郵件帳號（從環境變數讀取）
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')  # 郵件密碼（從環境變數讀取）
