import os
import secrets  # 用於生成隨機值，例如檔名
from flask import url_for, current_app
from PIL import Image  # 用於圖片處理
from app import mail
from flask_mail import Message

# 儲存使用者上傳的圖片，並生成縮圖
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)  # 生成隨機檔名前綴
    f_name, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext  # 新檔名
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)
    
    output_size = (125,125)
    i = Image.open(form_picture)  # 開啟圖片
    i.thumbnail(output_size)  # 調整圖片大小
    i.save(picture_path)  # 儲存圖片
    
    return picture_fn

# 發送重置密碼信件
def send_reset_email(user):
    token = user.get_reset_token()
    """
    # 實際寄信程式碼（註解掉，改用模擬）
    msg = Message('密碼重設請求',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''
    要重設密碼請點擊以下連結：
    {url_for('users.reset_token', token=token, _external=True)}

    如果您沒有提出此請求，請忽略此封信件。
    '''
    mail.send(msg)
    """
    print(f"模擬寄信給 {user.email}, token: {token}")
