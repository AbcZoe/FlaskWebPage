import os
import secrets  # 用於生成隨機值，例如檔名
from PIL import Image  # 用於圖片處理
from flask import request, render_template, url_for, flash, redirect, abort, jsonify
from app import app, db, bcrypt, mail
from app.forms import (RegistrationForm, LoginForm, UpdateAccountForm, 
                       PostForm, RequestResetForm, ResetPasswordForm)
from app.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message


# 首頁路由
@app.route("/")
def home():
    return render_template("home.html")


# 夜市頁面路由
@app.route("/nightMarket")
def nightMarket():
    return render_template("nightMarket.html")


# 註冊頁面路由
@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:  # 如果已登入，導回首頁
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():  # 表單驗證成功
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'帳號創建成功! 您現在可以登入了', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


# 登入頁面路由
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:  # 如果已登入，導回首頁
        return redirect(url_for('home'))
    form = LoginForm()
    print("form.errors:", form.errors)
    if form.validate_on_submit():
        # 查詢是否有使用者存在
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)  # 登入使用者
            next_page = request.args.get('next')  # 如果有重導頁面，跳轉回去
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('登入失敗. 請檢查電子郵件或密碼是否輸入錯誤', 'danger')
    return render_template('login.html', title='login', form=form)


# 登出路由
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


# 儲存使用者上傳的圖片，並生成縮圖
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)  # 生成隨機檔名前綴
    f_name, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext  # 新檔名
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    
    output_size = (125,125)
    i = Image.open(form_picture)  # 開啟圖片
    i.thumbnail(output_size)  # 調整圖片大小
    i.save(picture_path)  # 儲存圖片
    
    return picture_fn


# 帳號頁面
@app.route("/account", methods=['GET', 'POST'])
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
        return redirect(url_for('account'))
    elif request.method == 'GET':  # GET 請求，預設填入使用者資料
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='account', image_file=image_file, form=form)


# 新增貼文頁面，根據景點名稱
@app.route("/post/new/<spot_name>", methods=['GET', 'POST'])
@login_required
def new_post(spot_name):
    form = PostForm()
    if request.method == 'GET':
        form.spot.data = spot_name  # 自動帶入景點名稱
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, spot=form.spot.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('貼文創建成功', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form, legend='New Post')


# 傳送景點與貼文相關資料（API）
@app.route("/api/posts/<spot_name>")
def get_spot_posts(spot_name):
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(spot=spot_name)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    
    post_list = []
    for post in posts:
        post_list.append({
            "author": post.author.username,
            "author_image": url_for('static', filename='profile_pics/' + post.author.image_file),
            "title": post.title,
            "content": post.content,
            "date_posted": post.date_posted.strftime('%Y-%m-%d'),
            "id": post.id
        })
    return jsonify({
        "posts": post_list,
        "page": posts.page,
        "pages": posts.pages,
        "has_next": posts.has_next,
        "has_prev": posts.has_prev,
        "next_page": posts.next_num if posts.has_next else None,
        "prev_page": posts.prev_num if posts.has_prev else None
    })


# 顯示單篇貼文
@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)  # 查無資料會 404
    return render_template('post.html', title=post.title, post=post)


# 更新貼文
@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:  # 權限檢查
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.spot = form.spot.data
        post.content = form.content.data
        db.session.commit()
        flash('貼文更新成功', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':  # GET 請求，填入原本資料
        form.title.data = post.title
        form.spot.data = post.spot
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')


# 刪除貼文
@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('貼文已被刪除', 'success')
    return redirect(url_for('home'))


# 顯示某個使用者的所有貼文
@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
        # .order_by(Post.date_posted.desc())，按照 date_posted 欄位由新到舊排列
        # .paginate(page=page, per_page=5)，每頁最多顯示 5 筆貼文，page 是當前頁碼（從 URL 參數取得）。
    return render_template("user_posts.html", posts=posts, user=user)


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
    {url_for('reset_token', token=token, _external=True)}

    如果您沒有提出此請求，請忽略此封信件。
    '''
    mail.send(msg)
    """
    print(f"模擬寄信給 {user.email}, token: {token}")


# 重置密碼請求頁面
@app.route("/reset_request", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('我們已經寄出重設密碼的 email，請查看您的信箱。', 'info')
        return redirect(url_for('login'))
    return render_template("reset_request.html", title='Reset Password', form=form)


# 重置密碼頁面
@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Token 無效或已過期', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'密碼更新成功! 您現在可以登入了', 'success')
        return redirect(url_for('login'))
    return render_template("reset_token.html", title='Reset Password', form=form)
