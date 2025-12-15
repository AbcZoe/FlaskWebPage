from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

class PostForm(FlaskForm):
    title = StringField('標題', validators=[DataRequired()])
    spot = StringField('景點名稱', validators=[DataRequired()], render_kw={'readonly': True}) #render_kw={'readonly': True}，不要讓他改景點名稱，我們自動幫他填(不然他填錯可能會有問題)
    # render_kw={'readonly': True} 代表這個欄位不能修改，系統自動填入景點名稱
    content = TextAreaField('內容', validators=[DataRequired()])
    submit = SubmitField('上傳')
  