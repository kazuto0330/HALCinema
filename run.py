from flask import Flask , render_template , request, session, redirect, url_for, jsonify
from datetime import date
import mysql.connector
import json
import os



app = Flask(__name__)


app.secret_key ="himitukagi"



#セッションの暗号化
app.secret_key = 'secret_key'
#ユーザーデータの場所(とりあえず、次dbに)
USER_FILE = 'users.json'


# db接続用関数
def conn_db():
    conn = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="root",
        db="halcinemadb",
        charset="utf8"
    )
    return conn


def format_datetime(value, format='%Y年%m月%d日'):
    if value is None:
        return ''
    return value.strftime(format)

app.jinja_env.filters['strftime'] = format_datetime
    
    
#映画情報を複数件取得する関数（status="now_playing" or "coming_soon" , limit="取得件数" or "None"）
def fetch_movies(status='now_playing', limit=None):
    """条件に合致する映画データをデータベースから取得する関数
    Args:
        status (str): 'now_playing' なら現在公開中の映画、'coming_soon' なら今後公開予定の映画を取得。
        limit (int, optional): 取得する件数の上限。None ならすべて取得。
    Returns:
        list: 映画データのリスト
    """
    conn = None
    cursor = None
    try:
        conn = conn_db()
        cursor = conn.cursor(dictionary=True)
        today = date.today()
        query = ""
        params = ()  # パラメータの初期化を空のタプルにする

        if status == 'now_playing':
            query = """
                    SELECT
                        moviesId,
                        movieTitle,
                        movieReleaseDate,
                        movieEndDate,
                        movieRunningTime,
                        movieAudienceCount,
                        movieSynopsis,
                        movieImage
                    FROM
                        t_movies  
                    WHERE
                        movieEndDate >= %s AND movieReleaseDate <= %s
                    ORDER BY
                        movieAudienceCount DESC
                    """
            params = (today, today)
        elif status == 'coming_soon':
            query = """
                SELECT
                    moviesId,
                    movieTitle,
                    movieReleaseDate,
                    movieEndDate,
                    movieRunningTime,
                    movieAudienceCount,
                    movieSynopsis,
                    movieImage
                FROM
                    t_movies  
                WHERE
                    movieReleaseDate > %s
                ORDER BY
                    movieReleaseDate ASC
            """
            params = (today,)
        else:
            return []  # 不正な status が指定された場合は空のリストを返す

        if limit is not None and isinstance(limit, int) and limit > 0:
            query += " LIMIT %s"
            params = params + (limit,)  # limit をパラメータに追加
        elif limit is not None:
            print("Warning: limit は正の整数である必要があります。")

        cursor.execute(query, params)
        movies = cursor.fetchall()
        return movies
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
            
            
#イベント情報を複数件取得する関数（limit="取得件数" or "None" , random_order="True" or "False"）
def fetch_events(limit: int = 10, random_order: bool = False):
    """
    イベントテーブルから、今日以前に開始し、今日以降に終了するイベントを
    指定された件数だけ取得する関数
    オプション:
        limit (int): 取得するイベントの最大件数。デフォルトは10。
        random_order (bool): Trueの場合、取得順序をランダムにする。デフォルトはFalse（固定順序）。
    """
    conn = None
    cursor = None
    events = []
    today = date.today() # 今日の日付を取得

    try:
        conn = conn_db()
        cursor = conn.cursor(dictionary=True)

        # SQLクエリの基本部分
        sql_base = """
        SELECT
            eventInfoId,
            eventTitle,
            eventStartDate,
            eventEndDate,
            eventDescription,
            eventImage,
            eventUrl
        FROM
            t_event
        WHERE
            eventStartDate <= %s AND eventEndDate >= %s
        """
        
        # ORDER BY 句を動的に変更
        if random_order:
            order_by_clause = "ORDER BY RAND()"
        else:
            order_by_clause = "ORDER BY eventStartDate ASC, eventInfoId ASC"
            
        # LIMIT 句
        limit_clause = "LIMIT %s"

        # 完全なSQLクエリを構築
        sql = f"{sql_base} {order_by_clause} {limit_clause}"
        
        # SQLクエリを実行。パラメータはタプルで渡します。
        # `%s` プレースホルダはSQLインジェクション攻撃を防ぐために重要です。
        cursor.execute(sql, (today, today, limit))
        
        events = cursor.fetchall()

    except mysql.connector.Error as err:
        print(f"クエリ実行エラー: {err}")
    finally:
        # 接続とカーソルを必ず閉じる
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    return events


#指定したIDのイベントの詳細情報を取得する関数（）
def fetch_event_data(event_id):
    """指定したIDのイベントの詳細情報を取得する関数"""
    conn = None
    cursor = None
    events = []

    try:
        conn = conn_db()
        cursor = conn.cursor(dictionary=True)

        sql = """
            SELECT
                eventInfoId,
                eventTitle,
                eventStartDate,
                eventEndDate,
                eventDescription,
                eventImage,
                eventUrl
            FROM
                t_event
            WHERE
                eventInfoId = %s
        """
        
        cursor.execute(sql, (event_id,))
        
        events = cursor.fetchone()

    except mysql.connector.Error as err:
        print(f"クエリ実行エラー: {err}")
    finally:
        # 接続とカーソルを必ず閉じる
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    return events


#ユーザーデータを取得する関数（user_id）
def getUserData(user_id):
    """指定したIDのイベントの詳細情報を取得する関数"""
    conn = None
    cursor = None
    events = []

    try:
        conn = conn_db()
        cursor = conn.cursor(dictionary=True)

        sql = """
                SELECT
                    accountId,
                    accountName,
                    emailAddress,
                    password,
                    accountIcon,
                    realName,
                    phoneNumber,
                    birthDate
                FROM
                    t_account
                WHERE
                    accountId = %s;
        """
        
        cursor.execute(sql, (user_id,))
        
        events = cursor.fetchone()

    except mysql.connector.Error as err:
        print(f"クエリ実行エラー: {err}")
    finally:
        # 接続とカーソルを必ず閉じる
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    return events


#ユーザーデータを読み込む
def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    with open(USER_FILE, 'r') as f:
        return json.load(f)


#ユーザーデータを保存する
def save_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump(users, f)



############################################################################
### パスの定義
############################################################################

# TOPページ
@app.route('/')
def index():
    now_playing_movies = fetch_movies(status='now_playing', limit=10)
    coming_soon_movies = fetch_movies(status='coming_soon', limit=10)
    event = fetch_events(limit=10)
    return render_template("top.html", now_playing=now_playing_movies, coming_soon=coming_soon_movies, events=event)


# MOVIELIST(映画一覧)画面
@app.route('/movie_list')
def movie_list():
    now_playing_movies = fetch_movies(status='now_playing')
    coming_soon_movies = fetch_movies(status='coming_soon')
    return render_template("movie_list.html", now_playing=now_playing_movies, coming_soon=coming_soon_movies)


# EVENT画面
@app.route('/event/<int:event_id>')
def event(event_id):
    event = fetch_event_data(event_id)
    event_recommendation = fetch_events(limit=5,random_order=True) 
    return render_template("event.html", event=event, recommendation=event_recommendation) 


# PROFILE画面
@app.route('/profile')
def profile():
    user_id = 2
    userData = getUserData(user_id)
    print(userData)
    return render_template("profile.html", userData=userData)


# PROFILEのアップロード処理 (既存アカウントの更新)
@app.route('/add_account', methods=['POST'])
def update_profile():
    session['user_id'] = 2
    
    account_id = session.get('user_id') # セッションからユーザーIDを取得

    # ユーザーがログインしていない、またはセッションにIDがない場合
    if not account_id:
        return jsonify({'success': False, 'message': 'ログインが必要です。'}), 401


    data = request.get_json()

    # データが提供されていない場合
    if not data:
        return jsonify({'success': False, 'message': 'データが提供されていません。'}), 400


    # 必須項目の確認
    required_fields = ['accountName','realName', 'emailAddress', 'phoneNumber', 'birthDate']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'success': False, 'message': f'{field} は必須です。'}), 400

    # ------------------------------------------------------
    # 各データの取得と設定
    # ------------------------------------------------------
    account_Name = data['accountName']
    real_name = data['realName']
    email_address = data['emailAddress']
    phone_number = data['phoneNumber']

    # `birthDate` の型変換
    try:
        birth_date = date.fromisoformat(data['birthDate']) # JSから 'YYYY-MM-DD' 形式を想定
    except ValueError:
        return jsonify({'success': False, 'message': 'birthDate の形式が正しくありません。 (YYYY-MM-DD) 例: 1990-01-01'}), 400

    conn = None
    cursor = None
    try:
        # データベースに接続
        conn = conn_db()
        cursor = conn.cursor(dictionary=True) # dictionary=True で辞書形式で結果が返る

        sql = """
        UPDATE `t_account`
        SET
            `accountName` = %s,
            `emailAddress` = %s,
            `realName` = %s,
            `phoneNumber` = %s,
            `birthDate` = %s
        WHERE
            `accountId` = %s
        """
        values = (
            account_Name,
            email_address,
            real_name,
            phone_number,
            birth_date,
            account_id
        )

        # SQLを実行
        cursor.execute(sql, values)
        conn.commit() # 変更をコミット

        # 更新された行数をチェック
        if cursor.rowcount == 0:
            # 指定されたaccountIdのアカウントが存在しない、または更新する変更がなかった場合
            return jsonify({'success': False, 'message': 'プロフィールが見つからないか、更新する変更がありませんでした。'}), 404

        return jsonify({'success': True, 'message': 'プロフィールが正常に更新されました。'}), 200

    except mysql.connector.Error as err:
        # データベースエラーが発生した場合
        print(f"データベースエラー: {err}")
        if conn:
            conn.rollback() # エラー時はロールバック
        return jsonify({'success': False, 'message': f'データベースエラーが発生しました: {err}'}), 500
    except Exception as e:
        # その他の予期せぬエラーが発生した場合
        print(f"予期せぬエラー: {e}")
        return jsonify({'success': False, 'message': f'サーバーエラーが発生しました: {e}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# movie_information画面
@app.route('/movie_information/<int:movie_id>')
def movie_information(movie_id):
    return render_template("movie_information.html")


# guide画面
@app.route('/guide')
def guide():
    return render_template("guide.html")


# seat_reservation画面
@app.route('/seat_reservation')
def seat_reservation():
    return render_template("seat_reservation.html")


# member_login画面
@app.route('/member_login')
def member_login():
    return render_template("member_login.html")




# register画面

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()
        if username in users:
            return 'ユーザー名は既に存在します'
        users[username] = password 
        save_users(users)
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()
        if users.get(username) == password:
            session['username'] = username
            return render_template('top.html')
        return 'ユーザー名またはパスワードが間違っています'
    return render_template('login.html')





# pay画面
@app.route('/pay')
def pay():
    return render_template("pay.html")


# pay_comp画面
@app.route('/pay_comp')
def pay_comp():
    return render_template("pay_comp.html")


# member画面
@app.route('/member')
def member():
    return render_template("member.html")






#実行制御
if __name__ ==  "__main__":
    app.run(debug=True)