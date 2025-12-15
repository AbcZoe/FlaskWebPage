from flask import Flask, request,render_template,url_for,flash,redirect
from forms import RegistrationForm, LoginForm

app = Flask(__name__)

app.config['SECRET_KEY'] = 'eb5480089fb042e12832c2c09c9b22b9'

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
    if form.validate_on_submit():
        #用來測試已經有帳號的情況(因為我們還沒有要用資料庫)
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html',title='login',form=form)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)