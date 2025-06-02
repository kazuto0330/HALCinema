from flask import Flask , render_template , request
from datetime import date
import mysql.connector



app = Flask(__name__)

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
    
    print(event_id)
    print(event)
    
    return render_template("event.html", event=event, recommendation=event_recommendation) 


# PROFILE画面
@app.route('/profile')
def profile():
    return render_template("profile.html")


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


# login画面
@app.route('/login')
def login():
    return render_template("login.html")


# register画面
@app.route('/register')
def register():
    return render_template("register.html")


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