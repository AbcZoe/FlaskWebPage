from datetime import datetime  # 匯入 datetime，用於紀錄時間
from app import db, login_manager  # 匯入資料庫物件與登入管理器
from flask_login import UserMixin  # 匯入 UserMixin，用於 Flask-Login 支援的使用者功能
from flask import current_app  # 匯入 current_app，用於取得當前 Flask 應用設定
from itsdangerous import URLSafeTimedSerializer  # 匯入 itsdangerous，用於生成安全的 token

# Flask-Login 用來根據 user_id 載入使用者
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # 從資料庫取得對應 id 的使用者物件

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)  # 使用者唯一編號，主鍵
    username = db.Column(db.String(20), unique=True, nullable=False)  # 使用者名稱，不可重複
    email = db.Column(db.String(120), unique=True, nullable=False)  # 電子郵件，不可重複
    image_file = db.Column(db.String(20), nullable=False, default='userImage.png')  
    password = db.Column(db.String(60), nullable=False)  # 密碼（加密後）
    posta = db.relationship('Post', backref='author', lazy=True)  
    # 與 Post 模型建立一對多關聯，一個使用者可以有多篇文章
    # backref='author' 讓 Post 物件可以用 post.author 取得對應的 User

    # 產生重置密碼 token
    def get_reset_token(self, expires_sec=1800):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY']) # 建立序列化器
        # 使用 SECRET_KEY 生成安全序列化器
        return s.dumps({'user_id': self.id})  # 將使用者 id 編碼成 token

    # 驗證重置密碼 token
    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=expires_sec)['user_id']  
            # 解碼 token，檢查是否過期
        except Exception:
            return None  # 如果解碼失敗或過期，回傳 None
        return User.query.get(user_id)  # 成功則回傳對應的 User 物件

    # 物件的文字表示
    def __repr__(self):
        return f"User('{self.username}', '{this.email}', '{self.image_file}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # 文章唯一編號，主鍵
    title = db.Column(db.String(20), nullable=False)  # 文章標題，必填
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  
    # 發布日期，預設為目前 UTC 時間
    content = db.Column(db.Text, nullable=False)  # 文章內容，必填
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # 外鍵，對應 User.id，表示文章的作者 
    spot = db.Column(db.String(100), nullable=False)  # 景點名稱，必填

    # 物件的文字表示
    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"
