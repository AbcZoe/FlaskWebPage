import os  # 匯入操作系統模組，用於讀取環境變數
from flask import Flask  # 匯入 Flask 框架
from flask_sqlalchemy import SQLAlchemy  # 匯入 SQLAlchemy，用於資料庫操作
from flask_bcrypt import Bcrypt  # 匯入 Bcrypt，用於密碼加密
from flask_login import LoginManager  # 匯入 LoginManager，用於用戶登入管理
from flask_mail import Mail  # 匯入 Mail，用於發送郵件

# 建立 Flask 應用程式實例
app = Flask(__name__)

# 設定應用程式的密鑰，用於安全功能，例如 session 保護
app.config['SECRET_KEY'] = 'eb5480089fb042e12832c2c09c9b22b9'
# 設定資料庫 URI，這裡使用 SQLite，資料庫檔案名為 site.db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app) # 建立 SQLAlchemy 物件，用於操作資料庫
bcrypt = Bcrypt(app) # 建立 Bcrypt 物件，用於密碼加密與比對

# 建立 LoginManager 物件，用於管理使用者登入狀態
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # 設定未登入使用者要導向的登入頁面
login_manager.login_message_category = "info"  # 設定登入訊息的分類（用於顯示樣式）

# 設定郵件伺服器資訊
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'  # 郵件伺服器地址
app.config['MAIL_PORT'] = 587  # 郵件伺服器端口
app.config['MAIL_USE_TLS'] = True  # 使用 TLS 加密
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')  # 郵件帳號（從環境變數讀取）
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')  # 郵件密碼（從環境變數讀取）

# 建立 Mail 物件，用於發送郵件
mail = Mail(app)

# 匯入 routes 模組，將路由功能加入應用程式
from app import routes
