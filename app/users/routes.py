from flask import (request, render_template, url_for,
                   flash, redirect, Blueprint)
from app import db, bcrypt
from app.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm, 
                      RequestResetForm, ResetPasswordForm)
from app.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from app.users.utils import save_picture, send_reset_email

users = Blueprint('users', __name__)

# 註冊頁面路由
@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:  # 如果已登入，導回首頁
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():  # 表單驗證成功
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'帳號創建成功! 您現在可以登入了', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


# 登入頁面路由
@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:  # 如果已登入，導回首頁
        return redirect(url_for('main.home'))
    form = LoginForm()
    print("form.errors:", form.errors)
    if form.validate_on_submit():
        # 查詢是否有使用者存在
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)  # 登入使用者
            next_page = request.args.get('next')  # 如果有重導頁面，跳轉回去
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('登入失敗. 請檢查電子郵件或密碼是否輸入錯誤', 'danger')
    return render_template('login.html', title='login', form=form)


# 登出路由
@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))


# 帳號頁面
@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():  # 表單提交
        if form.picture.data:  # 如果有上傳新頭像
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('帳號內容已更新!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':  # GET 請求，預設填入使用者資料
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='account', image_file=image_file, form=form)


# 顯示某個使用者的所有貼文
@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
        # .order_by(Post.date_posted.desc())，按照 date_posted 欄位由新到舊排列
        # .paginate(page=page, per_page=5)，每頁最多顯示 5 筆貼文，page 是當前頁碼（從 URL 參數取得）。
    return render_template("user_posts.html", posts=posts, user=user)


# 重置密碼請求頁面
@users.route("/reset_request", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('我們已經寄出重設密碼的 email，請查看您的信箱。', 'info')
        return redirect(url_for('users.login'))
    return render_template("reset_request.html", title='Reset Password', form=form)


# 重置密碼頁面
@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Token 無效或已過期', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'密碼更新成功! 您現在可以登入了', 'success')
        return redirect(url_for('users.login'))
    return render_template("reset_token.html", title='Reset Password', form=form)
