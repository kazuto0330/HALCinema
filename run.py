import json
import os
import uuid
from pathlib import Path
import re
import random
from datetime import date, datetime, timedelta

import mysql.connector
from contextlib import contextmanager
from PIL import Image
from functools import wraps
from flask import Flask, render_template, request, session, redirect, url_for, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash


from urllib.parse import urlparse, urljoin

app = Flask(__name__)

# セッションの暗号化
app.secret_key = 'qawsedrftgyhujikolp'
# ユーザーデータの場所(とりあえず、次dbに)
USER_FILE = 'users.json'

IMAGE_SIZES = [(400, 400), (80, 80)]
app.config['USER_ICON_UPLOAD_FOLDER'] = 'static/images/usericon'
app.config['MOVIE_UPLOAD_FOLDER'] = 'static/images/movie'
app.config['EVENT_UPLOAD_FOLDER'] = 'static/images/event'

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 86400


# db接続用関数
def conn_db():
    """データベースに接続し、コネクションオブジェクトを返す"""
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="root",
            database="halcinemadb",
            charset="utf8"
        )
        return conn
    except mysql.connector.Error as err:
        print(f"データベース接続エラー: {err}")
        return None


# ----------------------------------------------------------------
#  DB接続とカーソル管理を行うコンテキストマネージャ
# ----------------------------------------------------------------
@contextmanager
def get_db_cursor():
    """
    データベース接続とカーソルを管理するコンテキストマネージャ。
    - with文と共に使用する。
    - 正常終了時は自動でコミットし、例外発生時はロールバックする。
    - 常にカーソルと接続をクローズする。
    """
    conn = None
    cursor = None
    try:
        conn = conn_db()
        if conn is None:
            # 接続に失敗した場合はNoneをyieldし、呼び出し元で処理させる
            yield None
            return

        cursor = conn.cursor(dictionary=True)
        # withブロックにカーソルを渡す
        yield cursor
        # withブロックの処理が正常に終了したらコミット
        conn.commit()

    except mysql.connector.Error as err:
        print(f"データベースエラー: {err}")
        # エラーが発生したらロールバック
        if conn:
            conn.rollback()
        # エラーを再度発生させ、呼び出し元に通知する
        raise err

    finally:
        # 常にカーソルと接続を閉じる
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def format_datetime(value, format='%Y年%m月%d日'):
    if value is None:
        return ''
    return value.strftime(format)


app.jinja_env.filters['strftime'] = format_datetime


# ログインしているか確認する関数
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session["url"] = request.url
        if 'user_id' not in session:
            return redirect(url_for('login'))
            
        return f(*args, **kwargs)
    return decorated_function


#ヘッダーに表示するデータを取得
@app.context_processor
def inject_user():
    if 'user_id' in session:
        user_id = session.get('user_id')
        sql = """
                SELECT
                    accountName, emailAddress, accountIcon
                FROM
                    t_account
                WHERE
                    accountId = %s;
        """
        user_info = []
        try:
            with get_db_cursor() as cursor:
                if cursor is None:
                    print("カーソルの取得に失敗しました。")
                    return []
                
                cursor.execute(sql, (user_id,))
                user_info = cursor.fetchone()
                print(user_info)

                # ここで返した辞書が、すべてのテンプレートのコンテキストに追加される
                return dict(user_data=user_info)

        except mysql.connector.Error:
            return dict(user_data=None)
    else:
        return dict(user_data=None)


# 映画情報を複数件取得する関数（status="now_playing" or "coming_soon" , limit="取得件数" or "None"）
def fetch_movies(status='now_playing', limit=None):
    """条件に合致する映画データをデータベースから取得する関数
    Args:
        status (str): 'now_playing' なら現在公開中の映画、'coming_soon' なら今後公開予定の映画を取得。
        limit (int, optional): 取得する件数の上限。None ならすべて取得。
    Returns:
        list: 映画データのリスト
    """
    try:
        today = date.today()
        query = ""
        params = ()  # パラメータの初期化を空のタプルにする

        if status == 'now_playing':
            query = """
                    SELECT 
                        moviesId, movieTitle, movieReleaseDate, movieEndDate, movieImage
                    FROM t_movies
                    WHERE movieEndDate >= %s
                      AND movieReleaseDate <= %s
                    ORDER BY movieAudienceCount DESC
                    """
            params = (today, today)
        elif status == 'coming_soon':
            query = """
                    SELECT 
                        moviesId, movieTitle, movieReleaseDate, movieEndDate, movieImage
                    FROM t_movies
                    WHERE movieReleaseDate > %s
                    ORDER BY movieReleaseDate ASC
                    """
            params = (today,)
        else:
            return []  # 不正な status が指定された場合は空のリストを返す

        if limit is not None and isinstance(limit, int) and limit > 0:
            query += " LIMIT %s"
            params = params + (limit,)  # limit をパラメータに追加
        elif limit is not None:
            print("Warning: limit は正の整数である必要があります。")

        with get_db_cursor() as cursor:
            if cursor is None:
                print("カーソルの取得に失敗しました。")
                return []

            cursor.execute(query, params)
            movies = cursor.fetchall()
            return movies
    except mysql.connector.Error:
        return []


# イベント情報を複数件取得する関数（limit="取得件数" or "None" , random_order="True" or "False"）
def fetch_events(limit: int = 10, random_order: bool = False):
    """
    イベントテーブルから、今日以前に開始し、今日以降に終了するイベントを
    指定された件数だけ取得する関数
    オプション:
        limit (int): 取得するイベントの最大件数。デフォルトは10。
        random_order (bool): Trueの場合、取得順序をランダムにする。デフォルトはFalse（固定順序）。
    """
    sql_base = """
                SELECT 
                    eventInfoId, eventTitle, eventImage
               FROM t_event
               WHERE eventStartDate <= %s
                 AND eventEndDate >= %s
               """
    events = []
    today = date.today()  # 今日の日付を取得

    try:
        if random_order:
            order_by_clause = "ORDER BY RAND()"
        else:
            order_by_clause = "ORDER BY eventStartDate ASC, eventInfoId ASC"
        # LIMIT 句
        limit_clause = "LIMIT %s"
        # 完全なSQLクエリを構築
        sql = f"{sql_base} {order_by_clause} {limit_clause}"

        with get_db_cursor() as cursor:
            if cursor is None:
                print("カーソルの取得に失敗しました。")
                return []

            cursor.execute(sql, (today, today, limit))
            events = cursor.fetchall()
            return events

    except mysql.connector.Error:
        print("error")
        return []


# 指定したIDのイベントの詳細情報を取得する関数（）
def fetch_event_data(event_id):
    sql = """
          SELECT 
            eventInfoId, eventTitle, eventStartDate, eventEndDate, eventDescription, eventImage, eventUrl
          FROM t_event
          WHERE eventInfoId = %s
          """
    try:
        with get_db_cursor() as cursor:
            if cursor is None:
                print("カーソルの取得に失敗しました。")
                return []

            cursor.execute(sql, (event_id,))
            events = cursor.fetchone()
            return events

    except mysql.connector.Error:
        return []


# ユーザーデータを取得する関数（user_id）
def getUserData(user_id):
    """指定したIDのイベントの詳細情報を取得する関数"""
    sql = """
          SELECT 
            accountId, accountName, emailAddress, password, accountIcon, realName, phoneNumber, birthDate, points
          FROM t_account
          WHERE accountId = %s; 
          """
    userData = []
    try:
        with get_db_cursor() as cursor:
            if cursor is None:
                print("カーソルの取得に失敗しました。")
                return []

            cursor.execute(sql, (user_id,))
            userData = cursor.fetchone()
            if 'points' in userData:
                if userData['points'] is None:
                    userData['points'] = 0

            return userData

    except mysql.connector.Error:
        return []


# ユーザーアイコンを取得する関数（user_id)
def getUserIcon(user_id):
    """指定したIDのユーザーアイコンを取得する関数"""
    sql = """
          SELECT accountIcon
          FROM t_account
          WHERE accountId = %s 
          """
    userIcon = None

    try:
        with get_db_cursor() as cursor:
            if cursor is None:
                print("カーソルの取得に失敗しました。")
                return []

            cursor.execute(sql, (user_id,))
            userIcon = cursor.fetchone()
            return userIcon

    except mysql.connector.Error:
        return None
    except Exception as e:
        print(f"Unexpected error in getUserIcon: {e}")
        return None


# ユーザーアイコンを保存する関数
def _save_icon_files(file_storage, base_upload_path: Path):
    """アップロードされた画像をリサイズして各ディレクトリに保存する。
    Args:
        file_storage: FlaskのFileStorageオブジェクト。
        base_upload_path: 保存先ディレクトリのベースパス(Pathオブジェクト)。

    Returns:
        str: 生成されたユニークなファイル名。
    
    Raises:
        IOError: 画像処理またはファイル保存に失敗した場合。
    """
    try:
        base_upload_path = Path(base_upload_path)
        img = Image.open(file_storage.stream)
        base_filename = f"{uuid.uuid4()}.jpg"

        for width, height in IMAGE_SIZES:
            dir_path = base_upload_path / f"{width}x{height}"
            dir_path.mkdir(parents=True, exist_ok=True) # ディレクトリが存在しなければ作成
            
            resized_img = img.resize((width, height), Image.Resampling.LANCZOS)
            save_path = dir_path / base_filename
            resized_img.convert('RGB').save(save_path, 'JPEG', quality=95)
        
        return base_filename
    except Exception as e:
        print(f"画像保存中にエラーが発生しました: {e}")
        raise IOError(f"画像ファイルの保存に失敗しました: {e}")


# ユーザーアイコンをデータベースに登録する関数
def _update_user_icon_in_db(account_id: int, new_filename: str):
    """
    データベースのユーザーアイコン情報を更新する。

    Args:
        account_id: 更新対象のユーザーID。
        new_filename: 新しいアイコンのファイル名。

    Raises:
        mysql.connector.Error: データベース操作に失敗した場合。
    """
    try:
        with get_db_cursor() as cursor:
            if cursor is None:
                print("カーソルの取得に失敗しました。")
                raise

            sql = "UPDATE `t_account` SET `accountIcon` = %s WHERE `accountId` = %s"
            cursor.execute(sql, (new_filename, account_id))
    
    except mysql.connector.Error as err:
        print(f"データベース更新エラー: {err}")
        raise # エラーを再送出して、呼び出し元で処理させる



# ユーザーアイコンを削除する関数 
def _delete_icon_files(filename: str, base_upload_path: Path):
    """
    指定されたファイル名の古いアイコン画像を全サイズ削除する。

    Args:
        filename: 削除するファイル名。
        base_upload_path: 保存先ディレクトリのベースパス(Pathオブジェクト)。
    """
    if not filename:
        return

    base_upload_path = Path(base_upload_path)
    print(f"古い画像ファイル {filename} の削除を開始します。")
    for width, height in IMAGE_SIZES:
        file_path = base_upload_path / f"{width}x{height}" / filename
        try:
            if file_path.exists():
                file_path.unlink() # os.remove(file_path) と同じ
                print(f"  - 削除成功: {file_path}")
            else:
                print(f"  - ファイルなし: {file_path}")
        except OSError as e:
            # 削除に失敗しても処理は続行するが、ログには残す
            print(f"エラー: 古い画像の削除に失敗しました。 Path: {file_path}, Error: {e}")


# 視聴履歴を取得する関数（user_id）
def watchHistory(user_id):
    """指定したIDの視聴履歴を取得する関数"""
    sql = """
          SELECT
            SR.*, SS.*, M.*
          FROM
              t_seatreservation AS SR
          JOIN
              t_scheduledshowing AS SS ON SR.scheduledShowingId = SS.scheduledShowingId
          JOIN
              t_movies AS M ON SS.moviesId = M.moviesId
          WHERE
              SR.accountId = %s
          ORDER BY
              SS.scheduledScreeningDate DESC, M.movieTitle ASC;
          """
    history_data = []  # 視聴履歴のリストを格納する変数
    try:
        with get_db_cursor() as cursor:
            if cursor is None:
                print("カーソルの取得に失敗しました。")
                return []

            cursor.execute(sql, (user_id,))
            history_data = cursor.fetchall()  # 複数行の結果を取得するため fetchall()
            return history_data

    except mysql.connector.Error:
        return []


#ポイントを保存する関数(user_id,points)
def savePoint(user_id, points):
    """ポイントを保存する関数"""
    try:
        with get_db_cursor() as cursor:
            if cursor is None:
                print("カーソルの取得に失敗しました。")
                return False

            # 現在のポイントを取得
            select_sql = "SELECT points FROM t_account WHERE accountId = %s"
            cursor.execute(select_sql, (user_id,))
            result = cursor.fetchone()

            current_points = result['points'] if result and result['points'] is not None else 0
            new_points = current_points + points

            # ポイントを更新
            update_sql = "UPDATE t_account SET points = %s WHERE accountId = %s"
            cursor.execute(update_sql, (new_points, user_id))
            return True

    except mysql.connector.Error as err:
        print(f"ポイント保存エラー: {err}")
        return False


# ユーザーデータを読み込む
def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    with open(USER_FILE, 'r') as f:
        return json.load(f)


# ユーザーデータを保存する
def save_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump(users, f)


# 支払い処理用の関数
def validate_credit_card(card_number, expiry_date, security_code, card_name):
    """クレジットカード情報のバリデーション"""
    errors = []

    # カード番号のバリデーション（数字のみ、16桁）
    card_number_clean = re.sub(r'\s+', '', card_number)
    if not re.match(r'^\d{16}$', card_number_clean):
        errors.append('カード番号は16桁の数字で入力してください')

    # 有効期限のバリデーション（MM/YY形式）
    if not re.match(r'^\d{2}/\d{2}$', expiry_date):
        errors.append('有効期限はMM/YY形式で入力してください')
    else:
        try:
            month, year = map(int, expiry_date.split('/'))
            if month < 1 or month > 12:
                errors.append('有効期限の月が正しくありません')

            # 現在年と比較（20XX年として処理）
            current_year = datetime.now().year % 100
            current_month = datetime.now().month
            if year < current_year or (year == current_year and month < current_month):
                errors.append('有効期限が過去の日付です')
        except ValueError:
            errors.append('有効期限の形式が正しくありません')

    # セキュリティコードのバリデーション（3桁の数字）
    if not re.match(r'^\d{3}$', security_code):
        errors.append('セキュリティコードは3桁の数字で入力してください')

    # カード名義のバリデーション
    if len(card_name.strip()) < 1:
        errors.append('カード名義を入力してください')
    elif not re.match(r'^[A-Za-z\s]+$', card_name):
        errors.append('カード名義は英字で入力してください')

    return errors


def validate_phone_number(phone_number):
    """電話番号のバリデーション（コンビニ払い用）"""
    # 日本の電話番号形式をチェック
    phone_clean = re.sub(r'[-\s()]', '', phone_number)
    if not re.match(r'^(0\d{9,10})$', phone_clean):
        return ['正しい電話番号を入力してください（例：090-1234-5678）']
    return []


def generate_payment_number():
    """コンビニ払い用の支払い番号を生成"""
    import random
    return f"{random.randint(10000000, 99999999):08d}"


def generate_paypay_qr():
    """PayPay用のQRコード情報を生成（ダミー）"""
    import uuid
    return f"paypay://pay/{str(uuid.uuid4())[:8]}"


# 支払い情報をデータベースに保存する関数（修正版）
def save_payment_info(user_id, payment_method, payment_data, amount):
    """支払い情報をデータベースに保存"""
    conn = None
    cursor = None
    try:
        conn = conn_db()
        cursor = conn.cursor()

        # テーブルが存在するかチェック
        cursor.execute("SHOW TABLES LIKE 't_payment'")
        table_exists = cursor.fetchone()

        if not table_exists:
            # テーブルが存在しない場合は作成
            create_table_sql = """
                               CREATE TABLE t_payment \
                               ( \
                                   paymentId     INT AUTO_INCREMENT PRIMARY KEY, \
                                   accountId     INT            NOT NULL, \
                                   paymentMethod VARCHAR(50)    NOT NULL, \
                                   paymentData   TEXT, \
                                   amount        DECIMAL(10, 2) NOT NULL, \
                                   paymentStatus VARCHAR(20)    NOT NULL DEFAULT 'pending', \
                                   createdAt     TIMESTAMP               DEFAULT CURRENT_TIMESTAMP
                               ) \
                               """
            cursor.execute(create_table_sql)
            print("t_payment テーブルを作成しました")

        sql = """
              INSERT INTO t_payment (accountId,
                                     paymentMethod,
                                     paymentData,
                                     amount,
                                     paymentStatus,
                                     createdAt)
              VALUES (%s, %s, %s, %s, %s, %s)
              """

        values = (
            user_id,
            payment_method,
            json.dumps(payment_data),  # JSON形式で保存
            amount,
            payment_data.get('status', 'pending'),  # 支払い状況：pending, completed, failed
            datetime.now()
        )

        cursor.execute(sql, values)
        conn.commit()

        return cursor.lastrowid  # 挿入されたレコードのIDを返す

    except mysql.connector.Error as err:
        print(f"Payment save error: {err}")
        if conn:
            conn.rollback()
        return None
    except Exception as e:
        print(f"Unexpected error in save_payment_info: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def get_screens():
    """スクリーンIDとスクリーンタイプを取得する関数

    Returns:
        list[dict]: スクリーン情報（screenId, screenType）のリスト
    """
    try:
        with get_db_cursor() as cursor:
            if cursor is None:
                print("カーソルの取得に失敗しました。")
                return []

            query = """
                    SELECT screenId, screenType
                    FROM t_screen
                    ORDER BY screenId \
                    """
            cursor.execute(query)
            screens = cursor.fetchall()  # DictCursor想定
            return screens
    except mysql.connector.Error as e:
        print("MySQL エラー:", e)
        return []


############################################################################
### パスの定義
############################################################################

#ログアウト
@app.route('/logout')
def logout():
    session.pop('user_id', None) # セッションからuser_idを削除
    session.pop('user', None)
    return redirect(url_for('index'))

# TOPページ
@app.route('/')
def index():
    screen_event = fetch_events(limit=5, random_order="True")
    now_playing_movies = fetch_movies(status='now_playing', limit=15)
    coming_soon_movies = fetch_movies(status='coming_soon', limit=15)
    event = fetch_events(limit=10)

    return render_template("top.html", screen_event=screen_event, now_playing=now_playing_movies,
                           coming_soon=coming_soon_movies, events=event)


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
    event_recommendation = fetch_events(limit=5, random_order=True)
    return render_template("event.html", event=event, recommendation=event_recommendation)


# PROFILE画面
@app.route('/profile')
@login_required
def profile():
    user_id = session.get('user_id')
    userData = getUserData(user_id)
    History = watchHistory(user_id)
    return render_template("profile.html", userData=userData, user_history=History)


# PROFILE画像のアップロード処理 (既存アカウントの更新)
@app.route('/add_account_img', methods=['POST'])
def update_profile_img():
    account_id = session.get('user_id')  # セッションからユーザーIDを取得

    # ユーザーがログインしていない、またはセッションにIDがない場合
    if not account_id:
        return jsonify({'success': False, 'message': 'ログインが必要です。'}), 401

    # 画像がない場合
    if 'croppedImage' not in request.files:
        return jsonify({'status': 'error', 'message': 'ファイルがありません'}), 400

    file = request.files['croppedImage']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'ファイルが選択されていません'}), 400


    # 1. 保存先のディレクトリパスを準備
    base_upload_path = app.config['USER_ICON_UPLOAD_FOLDER']
    new_filename = None

    try:
        # 手順1: 新しい画像を先に保存する
        new_filename = _save_icon_files(file, base_upload_path)

        # 手順2: 古い画像のファイル名を取得 (削除はまだしない)
        # ※getUserIconは既存の関数と仮定
        user_data = getUserIcon(account_id)
        old_filename = user_data.get('accountIcon') if user_data else None
        
        # 手順3: データベースを更新する
        _update_user_icon_in_db(account_id, new_filename)

        # 手順4: 全ての処理が成功した後、古い画像を削除する
        if old_filename:
            _delete_icon_files(old_filename, base_upload_path)
            
        # 8. 成功レスポンスを返す
        new_icon_url = url_for('static', filename=f'images/usericon/400x400/{new_filename}')
        return jsonify({'status': 'success', 'new_icon_url': new_icon_url})
    
    
    except (IOError, mysql.connector.Error, Exception) as e:
        # --- エラー発生時のロールバック処理 ---
        # 新しいファイルが作成された後でエラーが起きた場合、そのファイルを削除する
        if new_filename:
            print(f"エラー発生のため、ロールバック処理を実行します。作成されたファイル {new_filename} を削除します。")
            _delete_icon_files(new_filename, base_upload_path)
        
        # ユーザーに返すエラーメッセージ
        error_message = 'サーバーでエラーが発生しました。'
        if isinstance(e, IOError):
            error_message = '画像ファイルの処理中にエラーが発生しました。'
        elif isinstance(e, mysql.connector.Error):
            error_message = 'データベースの更新中にエラーが発生しました。'
        
        return jsonify({'status': 'error', 'message': error_message}), 500



# PROFILEのアップロード処理 (既存アカウントの更新)
@app.route('/add_account', methods=['POST'])
def update_profile():
    account_id = session.get('user_id')  # セッションからユーザーIDを取得

    # ユーザーがログインしていない、またはセッションにIDがない場合
    if not account_id:
        return jsonify({'success': False, 'message': 'ログインが必要です。'}), 401

    data = request.get_json()

    # データが提供されていない場合
    if not data:
        return jsonify({'success': False, 'message': 'データが提供されていません。'}), 400

    # 必須項目の確認
    required_fields = ['accountName', 'realName', 'emailAddress', 'phoneNumber', 'birthDate']
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
        birth_date = date.fromisoformat(data['birthDate'])  # JSから 'YYYY-MM-DD' 形式を想定
    except ValueError:
        return jsonify(
            {'success': False, 'message': 'birthDate の形式が正しくありません。 (YYYY-MM-DD) 例: 1990-01-01'}), 400

    conn = None
    cursor = None
    try:
        with get_db_cursor() as cursor:
            if cursor is None:
                print("カーソルの取得に失敗しました。")
                raise
            
            sql = """
                UPDATE `t_account`
                SET `accountName`  = %s,
                    `emailAddress` = %s,
                    `realName`     = %s,
                    `phoneNumber`  = %s,
                    `birthDate`    = %s
                WHERE `accountId` = %s
                """
            values = (
                account_Name,
                email_address,
                real_name,
                phone_number,
                birth_date,
                account_id
            )
            
            cursor.execute(sql, (values))
            
            # 更新された行数をチェック
            if cursor.rowcount == 0:
                # 指定されたaccountIdのアカウントが存在しない、または更新する変更がなかった場合
                return jsonify(
                    {'success': False, 'message': 'プロフィールが見つからないか、更新する変更がありませんでした。'}), 404

            return jsonify({'success': True, 'message': 'プロフィールが正常に更新されました。'}), 200
    
    
    except mysql.connector.Error as err:
        # データベースエラーが発生した場合
        print(f"データベースエラー: {err}")
        return jsonify({'success': False, 'message': f'データベースエラーが発生しました: {err}'}), 500
    except Exception as e:
        # その他の予期せぬエラーが発生した場合
        print(f"予期せぬエラー: {e}")


@app.route('/movie_information/<int:movie_id>')
def movie_information(movie_id):
    from collections import defaultdict

    with get_db_cursor() as cursor:
        if cursor is None:
            return "サーバー接続に失敗しました", 500

        # 映画情報を取得
        cursor.execute("""
                       SELECT moviesId,
                              movieTitle,
                              movieReleaseDate,
                              movieEndDate,
                              movieRunningTime,
                              movieSynopsis,
                              movieImage,
                              movieAudienceCount
                       FROM t_movies
                       WHERE moviesId = %s
                       """, (movie_id,))
        movie = cursor.fetchone()

        if not movie:
            return "映画が見つかりません", 404

        # スケジュール情報を取得（screenId を取得）
        cursor.execute("""
                       SELECT ss.scheduledShowingId,
                              ss.screenId,
                              ss.scheduledScreeningDate,
                              ss.screeningStartTime
                       FROM t_scheduledShowing ss
                       WHERE ss.moviesId = %s
                       ORDER BY ss.scheduledScreeningDate ASC, ss.screeningStartTime ASC
                       """, (movie_id,))
        schedules = cursor.fetchall()

        # 各上映予定の予約数を取得
        cursor.execute("""
            SELECT scheduledShowingId, COUNT(*) AS reservedCount
            FROM t_seatReservation
            GROUP BY scheduledShowingId
        """)
        reserved_map = {row['scheduledShowingId']: row['reservedCount'] for row in cursor.fetchall()}

        # スクリーンIDごとの座席数を定義
        seat_capacity_by_screen = {
            1: 200,
            2: 200,
            3: 200,
            4: 120,
            5: 120,
            6: 70,
            7: 70,
            8: 70
        }

        # スケジュールを日付ごとにグループ化
        schedule_by_day = defaultdict(list)

        for s in schedules:
            show_id = s['scheduledShowingId']
            screen_id = s['screenId']
            reserved = reserved_map.get(show_id, 0)
            total_seats = seat_capacity_by_screen.get(screen_id, 0)

            # 予約ステータスの判定
            if total_seats == 0:
                status = '?'
            elif reserved >= total_seats:
                status = '×'
            elif reserved >= total_seats * 0.8:
                status = '△'
            else:
                status = '○'

            s['reservationStatus'] = status

            # 日付キー（例：2025-01-15 (Wed)）
            date_str = s['scheduledScreeningDate'].strftime('%Y-%m-%d')
            weekday = s['scheduledScreeningDate'].strftime('%a')
            day_key = f"{date_str} ({weekday})"

            schedule_by_day[day_key].append(s)

        return render_template("movie_information.html",
                               movie=movie,
                               schedule=schedule_by_day)








# guide画面
@app.route('/guide')
def guide():
    return render_template("guide.html")


# seat_reservation画面
@app.route('/seat_reservation/<int:showing_id>', methods=['GET', 'POST'])
def seat_reservation(showing_id):
    if request.method == 'POST':
        data = request.get_json()
        seats = data.get('seats', [])  # [{ row: 'A', seatNumber: 3 }, ...]

        # ここではDBに予約を入れず、セッションに選択座席を保存するだけに変更
        session['selected_seats'] = seats
        session['showing_id'] = showing_id

        return jsonify({'message': '座席選択を受け付けました。次に支払い画面へ進んでください。'}), 200

    # GET時は予約済み座席を取得し、画面表示
    conn = conn_db()
    cursor = conn.cursor()

    # スクリーンIDを取得
    cursor.execute("SELECT screenId FROM t_scheduledShowing WHERE scheduledShowingId = %s", (showing_id,))
    result = cursor.fetchone()
    screenId = result[0]

    # 予約済み座席を取得（seatNumberカラムに'A-1'などが入っている想定）
    cursor.execute("""
        SELECT seatNumber FROM t_seatReservation
        WHERE scheduledShowingId = %s
    """, (showing_id,))
    reserved_seats = [row[0] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return render_template("seat_reservation.html", screenId=screenId, showing_id=showing_id, reserved_seats=reserved_seats)


# member_login画面
@app.route('/member_login')
def member_login():
    return render_template("member_login.html")


# register画面

def generate_unique_account_id():
    conn = conn_db()
    cursor = conn.cursor()
    while True:
        account_id = random.randint(10000, 99999)
        cursor.execute("SELECT COUNT(*) FROM t_account WHERE accountId = %s", (account_id,))
        if cursor.fetchone()[0] == 0:
            break
    cursor.close()
    conn.close()
    return account_id

import re

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        accountId = generate_unique_account_id()
        accountName = request.form.get('accountName')
        emailAddress = request.form.get('emailAddress')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        realName = request.form.get('realName')
        phoneNumber = request.form.get('phoneNumber')
        birthDate = request.form.get('birthDate')

        errors = {}

        # 必填项检查
        if not all([accountName, emailAddress, password, confirm_password, realName, phoneNumber, birthDate]):
            errors["general"] = "すべての必須項目を入力してください。"

        # 密码格式检查
        password_pattern = r"^(?=.*[a-zA-Z])(?=.*\d).{8,}$"
        if not re.match(password_pattern, password):
            errors["password"] = "パスワードは半角英数字を含む8文字以上で構成してください。"

        # 密码一致性检查
        if password != confirm_password:
            errors["confirm_password"] = "パスワードが一致しません。"

        # 邮箱格式检查
        if '@' not in emailAddress or '.' not in emailAddress:
            errors["emailAddress"] = "メールアドレスの形式が正しくありません。"

        # 电话格式检查
        if not re.match(r"^[0-9\s\+\-]+$", phoneNumber):
            errors["phoneNumber"] = "電話番号の形式が正しくありません。"

        if errors:
            return render_template('register.html', error="\n".join(errors.values()))

        # 密码加密
        hashed_password = generate_password_hash(password)

        # 插入数据库
        conn = conn_db()
        cursor = conn.cursor(buffered=True)
        sql = """
              INSERT INTO t_account (accountId, accountName, emailAddress, password,
                                     realName, phoneNumber, birthDate,
                                     accountIcon, points)
              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
              """
        values = (
            accountId, accountName, emailAddress, hashed_password,
            realName, phoneNumber, birthDate,
            "default.jpg", 0
        )
        cursor.execute(sql, values)
        conn.commit()
        cursor.close()
        conn.close()

        session['user'] = {
            'accountId': accountId,
            'accountName': accountName,
            'emailAddress': emailAddress
        }

        return redirect('/success')

    return render_template('register.html')




@app.route('/success')
def success():
    if 'user' in session:
        return render_template('success.html', user=session['user'])
    return redirect('/register')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['emailAddress']
        password = request.form['password']

        conn = conn_db()
        cursor = conn.cursor(buffered=True)
        cursor.execute("""
                       SELECT accountId, accountName, emailAddress, password, accountIcon, points
                       FROM t_account
                       WHERE emailAddress = %s
                       """, (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user[3], password):
            session['user'] = {
                'accountId': user[0],
                'accountName': user[1],
                'emailAddress': user[2],
                'accountIcon': user[4],
                'points': user[5]
            }
            session['user_id'] = user[0]
            
            if "url" in session:
                return redirect(session.pop('url',None))
            
            return redirect(url_for('index')) 
        else:
            error = "メールアドレスまたはパスワードが正しくありません。"
            return render_template('login.html', error=error)

    return render_template('login.html')




def inject_useraaaaa():
    if 'user_id' in session:
        user_id = session.get('user_id')
        sql = """
                SELECT
                    accountName,
                    emailAddress,
                    accountIcon
                FROM
                    t_account
                WHERE
                    accountId = %s;
        """
        user_info = []
        try:
            with get_db_cursor() as cursor:
                if cursor is None:
                    print("カーソルの取得に失敗しました。")
                    return []
                
                cursor.execute(sql, (user_id,))
                user_info = cursor.fetchone()
                print(user_info)

                # ここで返した辞書が、すべてのテンプレートのコンテキストに追加される
                return dict(user_data=user_info)

        except mysql.connector.Error:
            return dict(user_data=None)
    else:
        return dict(user_data=None)


# pay画面
# pay画面の修正版
@app.route('/pay')
@login_required  # ログインが必要
def pay():
    # セッションから座席情報と上映情報を取得
    seats = session.get('selected_seats')
    showing_id = session.get('showing_id')

    # 座席情報がない場合は座席選択ページにリダイレクト
    if not seats or not showing_id:
        return redirect(url_for('index'))  # または適切なページにリダイレクト

    # 料金計算（1席1800円として）
    total_amount = len(seats) * 1800
    session['total_amount'] = total_amount

    # 上映情報を取得
    sql = """
          SELECT ss.scheduledShowingId, \
                 ss.moviesId, \
                 ss.screenId, \
                 ss.scheduledScreeningDate, \
                 ss.screeningStartTime, \
                 m.movieTitle, \
                 m.movieImage, \
                 m.movieRunningTime, \
                 s.screenType
          FROM t_scheduledshowing AS ss \
                   JOIN \
               t_movies AS m ON ss.moviesId = m.moviesId \
                   JOIN \
               t_screen AS s ON ss.screenId = s.screenId
          WHERE ss.scheduledShowingId = %s; \
          """

    showing_info = None
    try:
        with get_db_cursor() as cursor:
            if cursor is None:
                print("カーソルの取得に失敗しました。")
                return redirect(url_for('index'))

            cursor.execute(sql, (showing_id,))
            showing_info = cursor.fetchone()

            if not showing_info:
                print("上映情報が見つかりません。")
                return redirect(url_for('index'))

            # 座席番号を文字列形式に変換（表示用）
            seat_labels = []
            for seat in seats:
                if isinstance(seat, dict):
                    # 辞書形式の場合（{'row': 'A', 'seatNumber': 1}）
                    seat_label = f"{seat.get('row')}-{seat.get('seatNumber')}"
                else:
                    # 文字列形式の場合（'A-1'）
                    seat_label = str(seat)
                seat_labels.append(seat_label)

            seats_display = ', '.join(seat_labels)

            return render_template("pay.html",
                                   seats=seats_display,
                                   seats_list=seats,  # JavaScriptで使用
                                   total_amount=total_amount,
                                   showing_info=showing_info)

    except mysql.connector.Error as e:
        print(f"データベースエラー: {e}")
        return redirect(url_for('index'))
    
    # return render_template("pay.html",seats=seats,showing_id=showing_id)


# 支払い処理のメインルート
@app.route('/process_payment', methods=['POST'])
def process_payment():
    try:
        # セッションからユーザーIDを取得
        user_id = session.get('user_id')

        # ログインチェックを緩和（開発・テスト用）
        if not user_id:
            # テスト用のデフォルトユーザーIDを設定
            user_id = 2
            print(f"Warning: ユーザーがログインしていません。テスト用ユーザーID {user_id} を使用します。")

        data = request.get_json()
        print(f"受信データ: {data}")

        if not data:
            return jsonify({
                'success': False,
                'message': 'データが送信されていません'
            }), 400

        payment_method = data.get('payment_method')

        # セッションから料金情報を取得（フロントエンドからの値より優先）
        amount = session.get('total_amount')
        seats = session.get('selected_seats', [])

        print(f"セッション情報:")
        print(f"  - total_amount: {amount}")
        print(f"  - selected_seats: {seats}")
        print(f"  - showing_id: {session.get('showing_id')}")

        if not amount:
            # セッションに料金情報がない場合はフロントエンドの値を使用
            amount = data.get('amount', 1800)
            print(f"Warning: セッションに料金情報がないため、フロントエンドの値を使用: {amount}円")
        else:
            print(f"セッションから料金情報を取得: {amount}円")

        # 料金の妥当性再チェック
        expected_amount = len(seats) * 1800 if seats else 1800
        print(f"料金検証: 期待値={expected_amount}円, セッション={amount}円")

        if seats and amount != expected_amount:
            print(f"Warning: 料金不整合 - 座席数{len(seats)}席 × 1800円 = {expected_amount}円 ≠ {amount}円")
            # セッションの料金を正しい値に修正
            amount = expected_amount
            session['total_amount'] = amount
            print(f"料金を修正: {amount}円")

        if not payment_method:
            return jsonify({
                'success': False,
                'message': '支払い方法を選択してください'
            }), 400

        payment_data = {}
        errors = []
        payment_status = 'pending'
        message = ''

        # 支払い方法別の処理
        if payment_method == 'credit-card':
            card_number = data.get('card_number', '')
            expiry_date = data.get('expiry_date', '')
            security_code = data.get('security_code', '')
            card_name = data.get('card_name', '')

            # バリデーション
            errors = validate_credit_card(card_number, expiry_date, security_code, card_name)

            if not errors:
                # クレジットカード情報を保存（実際のカード番号は保存しない）
                payment_data = {
                    'card_last4': card_number.replace(' ', '')[-4:] if len(card_number.replace(' ', '')) >= 4 else '',
                    'card_name': card_name,
                    'expiry_date': expiry_date
                }

                # 実際の決済処理のシミュレーション
                # import random
                # if random.random() > 0.1:  # 90%の確率で成功
                #     payment_status = 'completed'
                #     message = 'クレジットカード決済が完了しました'
                # else:
                #     payment_status = 'failed'
                #     message = 'クレジットカード決済に失敗しました'

                # テスト用に常に成功にする
                payment_status = 'completed'
                message = 'クレジットカード決済が完了しました'

        elif payment_method == 'convenience':
            phone_number = data.get('phone_number', '')

            # 電話番号のバリデーション（任意項目）
            if phone_number and phone_number.strip():
                errors = validate_phone_number(phone_number)

            if not errors:
                payment_number = generate_payment_number()
                payment_data = {
                    'payment_number': payment_number,
                    'phone_number': phone_number[-4:] if phone_number and len(phone_number) >= 4 else '',  # 下4桁のみ保存
                    'expire_date': (datetime.now().replace(hour=23, minute=59, second=59) +
                                    timedelta(days=3)).isoformat()  # 3日後まで有効
                }
                payment_status = 'completed'  # コンビニ払いは番号発行で完了とする
                message = f'コンビニ支払い番号を発行しました: {payment_number}'

        elif payment_method == 'paypay':
            qr_code = generate_paypay_qr()
            payment_data = {
                'qr_code': qr_code,
                'expire_time': (datetime.now() + timedelta(minutes=15)).isoformat()  # 15分後まで有効
            }
            payment_status = 'completed'  # PayPayもQRコード生成で完了とする
            message = 'PayPay決済用QRコードを生成しました'

        else:
            return jsonify({
                'success': False,
                'message': '無効な支払い方法です'
            }), 400

        # バリデーションエラーがある場合
        if errors:
            return jsonify({
                'success': False,
                'message': '入力内容に誤りがあります',
                'errors': errors
            }), 400

        # 支払い情報をデータベースに保存
        payment_data['status'] = payment_status
        payment_data['amount'] = amount  # 正しい金額を追加
        payment_data['seat_count'] = len(seats)  # 座席数も保存

        print(f"データベース保存: user_id={user_id}, method={payment_method}, amount={amount}円")
        payment_id = save_payment_info(user_id, payment_method, payment_data, amount)
        #ポイントの保存
        points = amount * 0.05#とりあえず5％
        savePoint(user_id, points)

        if not payment_id:
            return jsonify({
                'success': False,
                'message': 'データベースエラーが発生しました'
            }), 500

        # セッションに支払い情報を保存
        session['last_payment'] = {
            'payment_id': payment_id,
            'payment_method': payment_method,
            'status': payment_status,
            'data': payment_data,
            'message': message,
            'amount': amount,  # セッションから取得した正しい金額を保存
            'total_amount': amount,  # 明示的に total_amount も設定
            'seat_count': len(seats)
        }

        print(f"支払い処理完了: ID={payment_id}, 金額={amount}円, ステータス={payment_status}")

        return jsonify({
            'success': True,
            'message': message,
            'payment_id': payment_id,
            'payment_method': payment_method,
            'status': payment_status,
            'amount': amount,
            'data': payment_data
        })

    except Exception as e:
        print(f"Payment processing error: {e}")
        return jsonify({
            'success': False,
            'message': 'サーバーエラーが発生しました'
        }), 500


@app.route('/pay_comp')
def pay_comp():
    try:
        # セッションから支払い情報を取得
        payment_info = session.get('last_payment')
        print("支払い完了ページにアクセス")
        print(f"Payment info: {payment_info}")

        if not payment_info:
            # 支払い情報がない場合は支払いページにリダイレクト
            print("支払い情報が見つかりません。支払いページにリダイレクトします。")
            return redirect(url_for('pay'))

        # 支払いステータスが完了なら予約確定処理を実行
        if payment_info.get('status') == 'completed':
            # セッションから正しいキーでユーザーIDを取得
            accountId = session.get('user_id')  # 'accountId'ではなく'user_id'を使用
            seats = session.get('selected_seats', [])
            showing_id = session.get('showing_id')
            total_amount = session.get('total_amount', 0)

            print(
                f"予約処理開始: accountId={accountId}, seats={seats}, showing_id={showing_id}, total_amount={total_amount}")

            # 料金の整合性をチェック
            expected_amount = len(seats) * 1800 if seats else 0
            actual_amount = payment_info.get('amount', 0)

            print(
                f"料金チェック: 期待値={expected_amount}, 支払い情報の金額={actual_amount}, セッション金額={total_amount}")

            # 支払い情報の金額を正しい値に更新
            if total_amount and total_amount == expected_amount:
                payment_info['amount'] = total_amount
                payment_info['total_amount'] = total_amount
                print(f"料金を修正: {total_amount}円")
            elif actual_amount != expected_amount and expected_amount > 0:
                print(f"料金の不整合: 期待値={expected_amount}, 実際={actual_amount}")
                payment_info[
                    'warning_message'] = f"料金に不整合があります。期待値: {expected_amount}円, 支払い済み: {actual_amount}円"

            # 座席情報と上映情報が揃っている場合のみ予約処理を実行
            if seats and showing_id and accountId:
                conn = None
                cursor = None
                try:
                    conn = conn_db()
                    if conn is None:
                        print("データベース接続に失敗しました")
                        return render_template("pay_comp.html",
                                               payment_info=payment_info,
                                               error_message="データベース接続エラーが発生しました")

                    cursor = conn.cursor()

                    # 最大IDを取得（数値として）
                    cursor.execute("SELECT MAX(CAST(seatReservationId AS UNSIGNED)) FROM t_seatReservation")
                    result = cursor.fetchone()
                    max_id = result[0] if result[0] is not None else 0
                    next_id = max_id + 1

                    print(f"最大予約ID: {max_id}, 次のID: {next_id}")

                    # 各座席の予約を登録
                    reservation_ids = []
                    for seat in seats:
                        seat_label = f"{seat.get('row')}-{seat.get('seatNumber')}"
                        seatReservationId = f"{next_id:05d}"  # 5桁の文字列として保存

                        print(
                            f"予約登録: seatReservationId={seatReservationId}, showing_id={showing_id}, accountId={accountId}, seat_label={seat_label}")

                        cursor.execute("""
                                       INSERT INTO t_seatReservation (seatReservationId, scheduledShowingId, accountId, seatNumber)
                                       VALUES (%s, %s, %s, %s)
                                       """, (seatReservationId, showing_id, accountId, seat_label))

                        reservation_ids.append(seatReservationId)
                        next_id += 1

                    conn.commit()
                    print(f"予約登録完了: {reservation_ids}")

                    # 登録成功したらセッションの座席情報をクリア
                    session.pop('selected_seats', None)
                    session.pop('showing_id', None)
                    session.pop('total_amount', None)

                    # 予約情報を支払い情報に追加
                    payment_info['reservation_ids'] = reservation_ids
                    payment_info['reserved_seats'] = seats
                    payment_info['total_amount'] = total_amount

                except mysql.connector.Error as db_error:
                    if conn:
                        conn.rollback()
                    print(f"予約DB登録失敗: {db_error}")
                    return render_template("pay_comp.html",
                                           payment_info=payment_info,
                                           error_message="予約処理でエラーが発生しました。カスタマーサポートに連絡してください。")

                except Exception as e:
                    if conn:
                        conn.rollback()
                    print(f"予約処理で予期しないエラー: {e}")
                    return render_template("pay_comp.html",
                                           payment_info=payment_info,
                                           error_message="予約処理で予期しないエラーが発生しました。")

                finally:
                    if cursor:
                        cursor.close()
                    if conn and conn.is_connected():
                        conn.close()
            else:
                print(
                    f"予約に必要な情報が不足: seats={bool(seats)}, showing_id={bool(showing_id)}, accountId={bool(accountId)}")
                # 座席情報がない場合でも支払い完了画面は表示
                if not seats or not showing_id:
                    payment_info['warning_message'] = "座席予約情報が見つかりませんでした。支払いは完了していますが、座席予約の確認はカスタマーサポートまでお問い合わせください。"

        return render_template("pay_comp.html", payment_info=payment_info)

    except Exception as e:
        print(f"pay_comp関数で予期しないエラー: {e}")
        # エラーが発生した場合でも、最低限の情報で画面を表示
        return render_template("pay_comp.html",
                               payment_info=session.get('last_payment'),
                               error_message="ページの表示中にエラーが発生しました。")


# 支払い状況確認API
@app.route('/api/payment_status/<int:payment_id>')
def get_payment_status(payment_id):
    try:
        conn = conn_db()
        cursor = conn.cursor(dictionary=True)

        sql = """
              SELECT paymentId,
                     paymentMethod,
                     paymentStatus,
                     amount,
                     createdAt
              FROM t_payment
              WHERE paymentId = %s
              """

        cursor.execute(sql, (payment_id,))
        payment = cursor.fetchone()

        if not payment:
            return jsonify({
                'success': False,
                'message': '支払い情報が見つかりません'
            }), 404

        return jsonify({
            'success': True,
            'payment': payment
        })

    except mysql.connector.Error as err:
        print(f"Payment status error: {err}")
        return jsonify({
            'success': False,
            'message': 'データベースエラーが発生しました'
        }), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# 支払い方法別の詳細情報取得API
@app.route('/api/payment_details/<int:payment_id>')
def get_payment_details(payment_id):
    try:
        user_id = session.get('user_id', 2)

        conn = conn_db()
        cursor = conn.cursor(dictionary=True)

        sql = """
              SELECT paymentId,
                     paymentMethod,
                     paymentData,
                     paymentStatus,
                     amount,
                     createdAt
              FROM t_payment
              WHERE paymentId = %s
                AND accountId = %s
              """

        cursor.execute(sql, (payment_id, user_id))
        payment = cursor.fetchone()

        if not payment:
            return jsonify({
                'success': False,
                'message': '支払い情報が見つかりません'
            }), 404

        # JSON形式の支払いデータを解析
        payment_data = json.loads(payment['paymentData']) if payment['paymentData'] else {}
        payment['paymentData'] = payment_data

        return jsonify({
            'success': True,
            'payment': payment
        })

    except mysql.connector.Error as err:
        print(f"Payment details error: {err}")
        return jsonify({
            'success': False,
            'message': 'データベースエラーが発生しました'
        }), 500
    except json.JSONDecodeError:
        return jsonify({
            'success': False,
            'message': 'データ形式エラーが発生しました'
        }), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# member画面
@app.route('/member')
def member():
    return render_template("member.html")


# add_movie画面
@app.route('/add_movie', methods=['GET', 'POST'])
def add_movie():
    if request.method == 'POST':
        con = conn_db()
        cur = con.cursor()

        # ID作成
        cur.execute("SELECT MAX(moviesId) FROM t_movies")
        max_id = cur.fetchone()[0]
        if max_id:
            moviesId = f"{int(max_id) + 1:05}"
        else:
            moviesId = "00001"

        # 入力画面から値の受け取り
        movieTitle = request.form.get('movieTitle')
        movieReleaseDate = request.form.get('movieReleaseDate')
        movieEndDate = request.form.get('movieEndDate')
        movieRunningTime = request.form.get('movieRunningTime')
        movieSynopsis = request.form.get('movieSynopsis')

        errors = {}

        # 日付チェック
        if movieReleaseDate > movieEndDate:
            errors["date"] = "公開日が終了日より未来になっています。正しい日付を入力してください。"

        file = request.files.get('movieImage')
        if not file or file.filename == '':
            errors["movieImage"] = "画像が選択されていません。"

        # エラーがある場合はテンプレート再表示
        if errors:
            return render_template('add_movie.html', errors=errors)

        if file:
            try:
                # ベースの保存先パス
                base_upload_path = app.config['MOVIE_UPLOAD_FOLDER']
                path_original = os.path.join(base_upload_path, 'original')
                path_200h = os.path.join(base_upload_path, '200h')

                # 各フォルダがなければ作成
                os.makedirs(path_original, exist_ok=True)
                os.makedirs(path_200h, exist_ok=True)

                # ファイル名を生成
                base_filename = str(uuid.uuid4()) + '.jpg'

                # Pillowで画像を開く
                img = Image.open(file.stream)

                # オリジナル画像を保存
                img.convert('RGB').save(os.path.join(path_original, base_filename), 'JPEG', quality=95)

                # アスペクト比維持で縦200pxにリサイズ
                original_width, original_height = img.size
                target_height = 200
                target_width = int((target_height / original_height) * original_width)

                resized_img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)

                # リサイズ画像を保存
                resized_img.convert('RGB').save(os.path.join(path_200h, base_filename), 'JPEG', quality=95)

            finally:
                pass

        # データの挿入
        sql = """
              INSERT INTO t_movies (moviesId, \
                                    movieTitle, \
                                    movieReleaseDate, \
                                    movieEndDate, \
                                    movieRunningTime, \
                                    movieAudienceCount, \
                                    movieSynopsis, \
                                    movieImage) \
              VALUES (%(moviesId)s, \
                      %(movieTitle)s, \
                      %(movieReleaseDate)s, \
                      %(movieEndDate)s, \
                      %(movieRunningTime)s, \
                      %(movieAudienceCount)s, \
                      %(movieSynopsis)s, \
                      %(movieImage)s) \
              """
        data = {
            'moviesId': moviesId,
            'movieTitle': movieTitle,
            'movieReleaseDate': movieReleaseDate,
            'movieEndDate': movieEndDate,
            'movieRunningTime': movieRunningTime,
            'movieAudienceCount': 0,
            'movieSynopsis': movieSynopsis,
            'movieImage': base_filename
        }

        cur.execute(sql, data)

        con.commit()
        con.close()
        cur.close()
        
        flash("映画を追加しました。", "green")
        return redirect('/add_movie')

    return render_template("add_movie.html")


# add_event画面
@app.route('/add_event', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        con = conn_db()
        cur = con.cursor()

        # ID作成
        cur.execute("SELECT MAX(eventInfoId) FROM t_event")
        max_id = cur.fetchone()[0]
        if max_id:
            eventInfoId = f"{int(max_id) + 1:05}"
        else:
            eventInfoId = "00001"

        # 入力画面から値の受け取り
        eventTitle = request.form.get('eventTitle')
        eventStartDate = request.form.get('eventStartDate')
        eventEndDate = request.form.get('eventEndDate')
        eventDescription = request.form.get('eventDescription')
        eventUrl = request.form.get('eventUrl')

        errors = {}

        # 日付チェック
        if eventStartDate > eventEndDate:
            errors["date"] = "公開日が終了日より未来になっています。正しい日付を入力してください。"

        file = request.files.get('eventImage')
        if not file or file.filename == '':
            errors["eventImage"] = "画像が選択されていません。"

        # エラーがある場合はテンプレート再表示
        if errors:
            return render_template('add_event.html', errors=errors)

        if file:
            try:
                # ベースの保存先パス
                base_upload_path = app.config['EVENT_UPLOAD_FOLDER']
                path_original = os.path.join(base_upload_path, 'original')
                path_200h = os.path.join(base_upload_path, '200h')

                # 各フォルダがなければ作成
                os.makedirs(path_original, exist_ok=True)
                os.makedirs(path_200h, exist_ok=True)

                # ファイル名を生成
                base_filename = str(uuid.uuid4()) + '.jpg'

                # Pillowで画像を開く
                img = Image.open(file.stream)

                # オリジナル画像を保存
                img.convert('RGB').save(os.path.join(path_original, base_filename), 'JPEG', quality=95)

                # アスペクト比維持で縦150pxにリサイズ
                original_width, original_height = img.size
                target_height = 150
                target_width = int((target_height / original_height) * original_width)

                resized_img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)

                # リサイズ画像を保存
                resized_img.convert('RGB').save(os.path.join(path_200h, base_filename), 'JPEG', quality=95)

            finally:
                pass

        # データの挿入
        sql = """
              INSERT INTO t_event (eventInfoId, \
                                   eventTitle, \
                                   eventStartDate, \
                                   eventEndDate, \
                                   eventDescription, \
                                   eventImage, \
                                   eventUrl) \
              VALUES (%(eventInfoId)s, \
                      %(eventTitle)s, \
                      %(eventStartDate)s, \
                      %(eventEndDate)s, \
                      %(eventDescription)s, \
                      %(eventImage)s, \
                      %(eventUrl)s) \
              """
        data = {
            'eventInfoId': eventInfoId,
            'eventTitle': eventTitle,
            'eventStartDate': eventStartDate,
            'eventEndDate': eventEndDate,
            'eventDescription': eventDescription,
            'eventImage': base_filename,
            'eventUrl': eventUrl
        }

        cur.execute(sql, data)

        con.commit()
        con.close()
        cur.close()
        
        flash("イベントを追加しました。", "green")
        return redirect('/add_event')

    return render_template("add_event.html")


# add_screening画面
@app.route('/add_screening', methods=['GET', 'POST'])
def add_screening():
    if request.method == 'POST':
        con = conn_db()
        cur = con.cursor()

        # ID作成
        cur.execute("SELECT MAX(scheduledShowingId) FROM t_scheduledShowing")
        max_id = cur.fetchone()[0]
        if max_id:
            scheduledShowingId = f"{int(max_id) + 1:05}"
        else:
            scheduledShowingId = "00001"

        # 入力画面から値の受け取り
        moviesId = request.form.get('moviesId')
        screenId = request.form.get('screenId')
        scheduledScreeningDate = request.form.get('scheduledScreeningDate')
        screeningStartTimes = request.form.getlist('screeningStartTimes')  # 複数受け取り

        errors = {}

        if not screeningStartTimes:
            errors['screeningStartTimes'] = '上映開始時刻を1つ以上選択してください'

        # エラーあれば画面戻す
        if errors:
            now_playing = fetch_movies(status='now_playing')
            coming_soon = fetch_movies(status='coming_soon')
            movies = now_playing + coming_soon
            screens = get_screens()
            return render_template(
                'add_screening.html',
                errors=errors,
                movies=movies,
                screens=screens,
                movies_json=movies,
                selected_moviesId=moviesId,
                selected_screenId=screenId,
                selected_date=scheduledScreeningDate,
                
                selected_times=screeningStartTimes
            )

        # 複数時刻分、レコードを分けて挿入
        for start_time in screeningStartTimes:
            sql = """
                INSERT INTO t_scheduledShowing (
                    scheduledShowingId, moviesId, screenId, scheduledScreeningDate, screeningStartTime
                ) VALUES (
                    %(scheduledShowingId)s, %(moviesId)s, %(screenId)s, %(scheduledScreeningDate)s, %(screeningStartTime)s
                )
            """

            # IDはユニークなので、ループ毎にインクリメント（例）
            # ※実務ではもっと安全なID管理をしてください
            cur.execute("SELECT MAX(scheduledShowingId) FROM t_scheduledShowing")
            max_id = cur.fetchone()[0]
            if max_id:
                scheduledShowingId = f"{int(max_id) + 1:05}"
            else:
                scheduledShowingId = "00001"

            data = {
                'scheduledShowingId': scheduledShowingId,
                'moviesId': moviesId,
                'screenId': screenId,
                'scheduledScreeningDate': scheduledScreeningDate,
                'screeningStartTime': start_time
            }
            cur.execute(sql, data)

        con.commit()
        cur.close()
        con.close()

        # 登録成功後はリダイレクト推奨
        flash("上映予定を追加しました。", "green")
        return redirect('/add_screening')

    # GET時の映画とスクリーン取得
    now_playing = fetch_movies(status='now_playing')
    coming_soon = fetch_movies(status='coming_soon')
    movies = now_playing + coming_soon
    screens = get_screens()

    return render_template("add_screening.html", movies=movies, screens=screens, movies_json=movies)


# 実行制御
if __name__ == "__main__":
    app.run(debug=True)