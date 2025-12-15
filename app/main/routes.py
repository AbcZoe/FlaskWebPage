from flask import request, render_template, Blueprint

main = Blueprint('main', __name__)

# 首頁路由
@main.route("/")
def home():
    return render_template("home.html")

# 夜市頁面路由
@main.route("/nightMarket")
def nightMarket():
    return render_template("nightMarket.html")
