from flask import Flask  # 匯入 Flask 框架
from flask_sqlalchemy import SQLAlchemy  # 匯入 SQLAlchemy，用於資料庫操作
from flask_bcrypt import Bcrypt  # 匯入 Bcrypt，用於密碼加密
from flask_login import LoginManager  # 匯入 LoginManager，用於用戶登入管理
from flask_mail import Mail  # 匯入 Mail，用於發送郵件
from app.config import Config


db = SQLAlchemy() # 建立 SQLAlchemy 物件，用於操作資料庫
bcrypt = Bcrypt() # 建立 Bcrypt 物件，用於密碼加密與比對
# 建立 LoginManager 物件，用於管理使用者登入狀態
login_manager = LoginManager()
login_manager.login_view = 'users.login'  # 設定未登入使用者要導向的登入頁面
login_manager.login_message_category = "info"  # 設定登入訊息的分類（用於顯示樣式）
# 建立 Mail 物件，用於發送郵件
mail = Mail()

def create_app(config_class = Config):
    # 建立 Flask 應用程式實例
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    
    # 匯入 routes 模組，將路由功能加入應用程式
    from app.users.routes import users
    from app.posts.routes import posts
    from app.main.routes import main
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    
    return app
