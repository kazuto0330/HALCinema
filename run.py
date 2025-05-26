from flask import Flask , render_template , request
import mysql.connector



app = Flask(__name__)

# db接続用関数
def conn_db():
    conn = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="root",
        db="xxxDB",
        charset="utf8"
    )
    return conn



############################################################################
### パスの定義
############################################################################

# TOPページ
@app.route('/')
def index():
    return render_template("top.html")



# 新規登録ページ
@app.route('/register')
def register():
    return render_template("register.html")



# ログインページ
@app.route('/login')
def login():
    return render_template("login.html")



# 映画情報ページ
@app.route('/movie_information')
def movie_information():
    return render_template("movie_information.html")



# イベントページ
@app.route('/event')
def event():
    return render_template("event.html")



# 座席予約ページ
@app.route('/seat_reservation')
def seat_reservation():
    return render_template("seat_reservation.html")


























#実行制御
if __name__ ==  "__main__":
    app.run(debug=True, port=2000)