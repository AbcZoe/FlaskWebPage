from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError # 表單驗證器
from app.models import User # 匯入使用者模型，用於驗證使用者是否存在
from flask_login import current_user # 目前登入的使用者資訊

class RegistrationForm(FlaskForm):
    username = StringField('使用者名稱',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField("電子郵件", validators=[DataRequired(), Email()])
    password = PasswordField("密碼", validators=[DataRequired()])
    confirm_password = PasswordField("確認密碼", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('註冊')
    # 驗證使用者名稱是否已存在
    def validate_username(self,username):
        user = User.query.filter_by(username=username.data).first() 
        #尋找資料庫中第一個與輸入一樣的信箱，並拿取那一個(欄)的物件
        if user:
            raise ValidationError('該使用者名稱已有人使用. 請選擇另一個.')
    # 驗證電子郵件是否已存在
    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('該電子郵件已有人使用. 請選擇另一個.')

class LoginForm(FlaskForm):
    email = StringField("電子郵件", validators=[DataRequired(), Email()])
    password = PasswordField("密碼", validators=[DataRequired()])
    remember = BooleanField("記住密碼")
    submit = SubmitField('登入')

class UpdateAccountForm(FlaskForm):
    username = StringField('使用者名稱',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField("電子郵件", validators=[DataRequired(), Email()])
    picture = FileField("更換頭像", validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('更新')
    # 驗證使用者名稱是否已被其他使用者使用
    def validate_username(self,username):
        if username.data != current_user.username: # 如果有改變名稱
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('該使用者名稱已有人使用. 請選擇另一個.')
    # 驗證電子郵件是否已被其他使用者使用
    def validate_email(self,email):
        if email.data != current_user.email: # 如果有改變 email
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('該電子郵件已有人使用. 請選擇另一個.')

class PostForm(FlaskForm):
    title = StringField('標題', validators=[DataRequired()])
    spot = StringField('景點名稱', validators=[DataRequired()], render_kw={'readonly': True}) #render_kw={'readonly': True}，不要讓他改景點名稱，我們自動幫他填(不然他填錯可能會有問題)
    # render_kw={'readonly': True} 代表這個欄位不能修改，系統自動填入景點名稱
    content = TextAreaField('內容', validators=[DataRequired()])
    submit = SubmitField('上傳')

class RequestResetForm(FlaskForm):
    email = StringField("電子郵件", validators=[DataRequired(), Email()])
    submit = SubmitField('送出請求')
    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('該電子郵件並沒有帳號. 請先註冊.')    

class ResetPasswordForm(FlaskForm):
    password = PasswordField("密碼", validators=[DataRequired()])
    confirm_password = PasswordField("確認密碼", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('更新密碼')
    