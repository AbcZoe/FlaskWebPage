from flask import request, render_template,url_for,flash,redirect
from app import app
from app.forms import RegistrationForm, LoginForm
from app.models import User, Post

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/nightMarket")
def nightMarket():
    return render_template("nightMarket.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html',title='Register',form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    print("form.errors:", form.errors)
    if form.validate_on_submit():
        #用來測試已經有帳號的情況(因為我們還沒有要用資料庫)
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html',title='login',form=form)
