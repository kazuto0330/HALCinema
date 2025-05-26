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
            
            
            
def fetch_events(limit: int = 10):
    """
    イベントテーブルから、今日以前に開始し、今日以降に終了するイベントを
    指定された件数だけ取得する関数
    """
    conn = None
    cursor = None
    events = []
    today = date.today() # 今日の日付を取得

    try:
        conn = conn_db()
        cursor = conn.cursor(dictionary=True)
        today = date.today()

        # cursor(dictionary=True) を使うと、結果を辞書形式で取得でき、カラム名でアクセスしやすくなります
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
            eventStartDate <= %s AND eventEndDate >= %s
        ORDER BY
            eventStartDate ASC, eventInfoId ASC -- 開始日でソート、次にIDでソート
        LIMIT %s
        """
        
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





############################################################################
### パスの定義
############################################################################

# TOPページ
@app.route('/')
def index():
        # トップページで映画データを表示する
        now_playing_movies = fetch_movies(status='now_playing', limit=10)
        coming_soon_movies = fetch_movies(status='coming_soon', limit=10)
        event = fetch_events(limit=10)
        print(f"now_playing_movies: {now_playing_movies}")
        print(f"Coming Soon Movies: {coming_soon_movies}")
        print(f"Event : {event}")
        return render_template("top.html", now_playing=now_playing_movies, coming_soon=coming_soon_movies, events=event)

# EVENT画面
@app.route('/event')
def event():
    return render_template("event.html")

# PROFILE画面
@app.route('/profile')
def profile():
    return render_template("profile.html")



# movie_information画面
@app.route('/movie_information')
def movie_information():
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




#実行制御
if __name__ ==  "__main__":
    app.run(debug=True, port=2000)