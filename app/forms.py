from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User
from flask_login import current_user

class RegistrationForm(FlaskForm):
    username = StringField('使用者名稱',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField("電子郵件", validators=[DataRequired(), Email()])
    password = PasswordField("密碼", validators=[DataRequired()])
    confirm_password = PasswordField("確認密碼", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('註冊')
    
    def validate_username(self,username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('該使用者名稱已有人使用. 請選擇另一個.')

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
    
    def validate_username(self,username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('該使用者名稱已有人使用. 請選擇另一個.')

    def validate_email(self,email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('該電子郵件已有人使用. 請選擇另一個.')

class PostForm(FlaskForm):
    title = StringField('標題', validators=[DataRequired()])
    spot = StringField('景點名稱', validators=[DataRequired()], render_kw={'readonly': True}) #render_kw={'readonly': True}，不要讓他改景點名稱，我們自動幫他填(不然他填錯可能會有問題)
    content = TextAreaField('內容', validators=[DataRequired()])
    submit = SubmitField('上傳')
