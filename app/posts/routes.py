from flask import (request, render_template, url_for,
                   flash, redirect, abort, jsonify, Blueprint)
from app import db
from flask_login import current_user, login_required
from app.posts.forms import  PostForm
from app.models import  Post

posts = Blueprint('posts', __name__)

# 新增貼文頁面，根據景點名稱
@posts.route("/post/new/<spot_name>", methods=['GET', 'POST'])
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
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='New Post', form=form, legend='New Post')


# 傳送景點與貼文相關資料（API）
@posts.route("/api/posts/<spot_name>")
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
@posts.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)  # 查無資料會 404
    return render_template('post.html', title=post.title, post=post)


# 更新貼文
@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
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
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':  # GET 請求，填入原本資料
        form.title.data = post.title
        form.spot.data = post.spot
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')


# 刪除貼文
@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('貼文已被刪除', 'success')
    return redirect(url_for('main.home'))
