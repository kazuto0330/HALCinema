import json
import os
import uuid
import re
from datetime import date, datetime, timedelta

import mysql.connector
from contextlib import contextmanager
from PIL import Image
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)


#セッションの暗号化
app.secret_key = 'qawsedrftgyhujikolp'
#ユーザーデータの場所(とりあえず、次dbに)
USER_FILE = 'users.json'

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
                    SELECT moviesId,
                           movieTitle,
                           movieReleaseDate,
                           movieEndDate,
                           movieImage
                    FROM t_movies
                    WHERE movieEndDate >= %s
                      AND movieReleaseDate <= %s
                    ORDER BY movieAudienceCount DESC
                    """
            params = (today, today)
        elif status == 'coming_soon':
            query = """
                    SELECT moviesId,
                           movieTitle,
                           movieReleaseDate,
                           movieEndDate,
                           movieImage
                    FROM t_movies
                    WHERE movieReleaseDate > %s
                    ORDER BY movieReleaseDate ASC \
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
                SELECT eventInfoId,
                        eventTitle,
                        eventImage
                FROM t_event
                WHERE eventStartDate <= %s
                    AND eventEndDate >= %s \
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
            SELECT eventInfoId,
                    eventTitle,
                    eventStartDate,
                    eventEndDate,
                    eventDescription,
                    eventImage,
                    eventUrl
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
                accountId,
                accountName,
                emailAddress,
                password,
                accountIcon,
                realName,
                phoneNumber,
                birthDate,
                points
            FROM
                t_account
            WHERE
                accountId = %s;
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


#視聴履歴を取得する関数（user_id）
def watchHistory(user_id):
    """指定したIDの視聴履歴を取得する関数"""
    sql = """
            SELECT
                A.accountName AS accountName,
                M.movieTitle AS movieTitle,
                M.movieImage AS movieImage, -- 映画の画像ファイル名を追加
                SS.scheduledScreeningDate AS scheduledScreeningDate,
                SR.seatNumber AS seatNumber,
                SS.screenId AS screenId -- スクリーンIDを追加
            FROM
                t_account AS A
            JOIN
                t_seatreservation AS SR ON A.accountId = SR.accountId
            JOIN
                t_scheduledshowing AS SS ON SR.scheduledShowingId = SS.scheduledShowingId
            JOIN
                t_movies AS M ON SS.moviesId = M.moviesId
            WHERE
                A.accountId = %s
            ORDER BY
                SS.scheduledScreeningDate DESC, M.movieTitle ASC;
    """
    history_data = [] # 視聴履歴のリストを格納する変数
    try:
        with get_db_cursor() as cursor:
            if cursor is None:
                print("カーソルの取得に失敗しました。")
                return []

            cursor.execute(sql, (user_id,))
            history_data = cursor.fetchall() # 複数行の結果を取得するため fetchall()
            return history_data

    except mysql.connector.Error:
        return []


#ユーザーデータを読み込む
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
            if year < current_year:
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
        return ['正しい電話番号を入力してください']
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
            'pending',  # 支払い状況：pending, completed, failed
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
                ORDER BY screenId
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

# ユーザーアイコン取得API（修正版）
@app.route('/api/user_icon', methods=['GET'])
def get_icon():
    try:
        Icon = getUserIcon(session.get('user_id'))

        if Icon is None:
            return jsonify({
                'success': False,
                'message': 'ユーザーが見つかりません',
                'accountIcon': None
            }), 404

        return jsonify({
            'success': True,
            'accountIcon': Icon.get('accountIcon', None)
        })

    except Exception as e:
        print(f"User icon error: {e}")
        return jsonify({
            'success': False,
            'message': 'サーバーエラーが発生しました',
            'accountIcon': None
        }), 500


# TOPページ
@app.route('/')
def index():
    session['user_id'] = 2
    
    screen_event = fetch_events(limit=5, random_order="True")
    now_playing_movies = fetch_movies(status='now_playing', limit=15)
    coming_soon_movies = fetch_movies(status='coming_soon', limit=15)
    event = fetch_events(limit=10)
    
    return render_template("top.html", screen_event=screen_event, now_playing=now_playing_movies, coming_soon=coming_soon_movies, events=event)


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
def profile():
    user_id = 2
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

    if 'croppedImage' not in request.files:
        return jsonify({'status': 'error', 'message': 'ファイルがありません'}), 400

    file = request.files['croppedImage']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'ファイルが選択されていません'}), 400

    if file:
        try:
            # 1. 保存先のディレクトリパスを準備
            base_upload_path = app.config['USER_ICON_UPLOAD_FOLDER']
            path_400 = os.path.join(base_upload_path, '400x400')
            path_80 = os.path.join(base_upload_path, '80x80')

            # 2. ディレクトリが存在しなければ作成
            os.makedirs(path_400, exist_ok=True)
            os.makedirs(path_80, exist_ok=True)

            # 3. Pillowで画像を開く
            img = Image.open(file.stream)

            # 4. ユニークなファイル名を生成
            base_filename = str(uuid.uuid4()) + '.jpg'

            # 5. 古い画像があれば削除
            userData = getUserIcon(account_id)
            oldImg = userData['accountIcon']
            if oldImg:
                old_full_filename = oldImg
                old_filepath_400 = os.path.join(path_400, old_full_filename)
                old_filepath_80 = os.path.join(path_80, old_full_filename)

                if os.path.exists(old_filepath_400):  # 400x400 ディレクトリ内の古い画像を削除
                    try:
                        os.remove(old_filepath_400)
                        print(f"古い画像 {old_filepath_400} を削除しました。")
                    except OSError as e:
                        print(f"エラー: 古い画像 {old_filepath_400} の削除中に問題が発生しました: {e}")
                else:
                    print(f"古い画像 {old_filepath_400} は存在しませんでした。")

                if os.path.exists(old_filepath_80):  # 80x80 ディレクトリ内の古い画像を削除
                    try:
                        os.remove(old_filepath_80)
                        print(f"古い画像 {old_filepath_80} を削除しました。")
                    except OSError as e:
                        print(f"エラー: 古い画像 {old_filepath_80} の削除中に問題が発生しました: {e}")
                else:
                    print(f"古い画像 {old_filepath_80} は存在しませんでした。")

            # 6. 画像をリサイズして保存
            img_400 = img.resize((400, 400), Image.Resampling.LANCZOS)
            img_80 = img.resize((80, 80), Image.Resampling.LANCZOS)

            img_400.convert('RGB').save(os.path.join(path_400, base_filename), 'JPEG', quality=95)
            img_80.convert('RGB').save(os.path.join(path_80, base_filename), 'JPEG', quality=95)

            # 7. データベースのユーザー情報を更新
            conn = None
            cursor = None
            try:
                # データベースに接続
                conn = conn_db()
                cursor = conn.cursor(dictionary=True)  # dictionary=True で辞書形式で結果が返る

                sql = """
                UPDATE `t_account`
                SET`accountIcon` = %s
                WHERE`accountId` = %s
                """
                values = (base_filename, account_id)

                # SQLを実行
                cursor.execute(sql, values)
                conn.commit()  # 変更をコミット

            except mysql.connector.Error as err:
                print(f"データベースエラー: {err}")
                if conn:
                    conn.rollback()  # ロールバック
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

            # 8. フロントエンドに返す新しい画像のURLを生成
            new_icon_url = url_for('static', filename=f'images/usericon/400x400/{base_filename}')

            return jsonify({'status': 'success', 'new_icon_url': new_icon_url})

        except Exception as e:
            print(f"Error during image processing: {e}")
            return jsonify({'status': 'error', 'message': 'サーバーエラーが発生しました'}), 500

    return jsonify({'status': 'error', 'message': '不明なエラー'}), 500


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
        # データベースに接続
        conn = conn_db()
        cursor = conn.cursor(dictionary=True)  # dictionary=True で辞書形式で結果が返る

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

        # SQLを実行
        cursor.execute(sql, values)
        conn.commit()  # 変更をコミット

        # 更新された行数をチェック
        if cursor.rowcount == 0:
            # 指定されたaccountIdのアカウントが存在しない、または更新する変更がなかった場合
            return jsonify(
                {'success': False, 'message': 'プロフィールが見つからないか、更新する変更がありませんでした。'}), 404

        return jsonify({'success': True, 'message': 'プロフィールが正常に更新されました。'}), 200

    except mysql.connector.Error as err:
        # データベースエラーが発生した場合
        print(f"データベースエラー: {err}")
        if conn:
            conn.rollback()  # エラー時はロールバック
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
    movie_db = {
        1: {
            "title": "名探偵コナン<br>隻眼の残像",
            "release": "2025年6月1日",
            "poster": "images/conan.png",
            "description": (
                "長野県・八ヶ岳連峰未宝岳。長野県警の大和敢助が雪山で“ある男”を追っていた時、"
                "不意に何者かの影が敢助の視界に。気をとられた瞬間、“ある男”が放ったライフル弾が"
                "敢助の左眼をかすめ、大きな地響きとともに雪崩が発生。そのまま敢助を飲み込んでしまい......。"
                "10カ月後。国立天文台野辺山の施設研究員が何者かに襲われたという通報を受け、"
                "雪崩から奇跡的に生還した敢助と、上原由衣が現場へ駆けつけた。"
            ),
            "duration": "110分",
            "schedule": {
                "Mon": {
                    "month": "11",
                    "day": "11",
                    "week": "Mon",
                    "slots": [
                        {"label": "A", "time": "10:00〜12:00", "status": "〇"},
                        {"label": "B", "time": "11:00〜13:00", "status": "✕"},
                        {"label": "D", "time": "10:00〜12:00", "status": "△"},
                        {"label": "C", "time": "11:00〜13:00", "status": "〇"},
                        {"label": "E", "time": "10:00〜12:00", "status": "✕"},
                    ]
                },
                "Tue": {
                    "month": "11",
                    "day": "12",
                    "week": "Tue",
                    "slots": [
                        {"label": "A", "time": "10:00〜12:00", "status": "△"},
                        {"label": "B", "time": "11:00〜13:00", "status": "✕"},
                        {"label": "D", "time": "10:00〜12:00", "status": "〇"},
                        {"label": "C", "time": "11:00〜13:00", "status": "〇"},
                        {"label": "E", "time": "10:00〜12:00", "status": "〇"},
                    ]
                },
                "Wed": {
                    "month": "11",
                    "day": "13",
                    "week": "Wed",
                    "slots": [
                        {"label": "A", "time": "10:00〜12:00", "status": "〇"},
                        {"label": "B", "time": "11:00〜13:00", "status": "〇"},
                        {"label": "D", "time": "10:00〜12:00", "status": "〇"},
                        {"label": "C", "time": "11:00〜13:00", "status": "〇"},
                        {"label": "E", "time": "10:00〜12:00", "status": "〇"},
                    ]
                },
                "Thu": {
                    "month": "11",
                    "day": "14",
                    "week": "Thu",
                    "slots": [
                        {"label": "A", "time": "10:00〜12:00", "status": "〇"},
                        {"label": "B", "time": "11:00〜13:00", "status": "〇"},
                        {"label": "D", "time": "10:00〜12:00", "status": "〇"},
                        {"label": "C", "time": "11:00〜13:00", "status": "〇"},
                        {"label": "E", "time": "10:00〜12:00", "status": "〇"},
                    ]
                },
                "Fri": {
                    "month": "11",
                    "day": "15",
                    "week": "Fri",
                    "slots": [
                        {"label": "A", "time": "10:00〜12:00", "status": "〇"},
                        {"label": "B", "time": "11:00〜13:00", "status": "〇"},
                        {"label": "D", "time": "10:00〜12:00", "status": "〇"},
                        {"label": "C", "time": "11:00〜13:00", "status": "〇"},
                        {"label": "E", "time": "10:00〜12:00", "status": "〇"},
                    ]
                },
                "Sat": {
                    "month": "11",
                    "day": "16",
                    "week": "Sat",
                    "slots": [
                        {"label": "A", "time": "10:00〜12:00", "status": "〇"},
                        {"label": "B", "time": "11:00〜13:00", "status": "〇"},
                        {"label": "D", "time": "10:00〜12:00", "status": "〇"},
                        {"label": "C", "time": "11:00〜13:00", "status": "〇"},
                        {"label": "E", "time": "10:00〜12:00", "status": "〇"},
                    ]
                },
                "Sun": {
                    "month": "11",
                    "day": "17",
                    "week": "Sun",
                    "slots": [
                        {"label": "A", "time": "10:00〜12:00", "status": "〇"},
                        {"label": "B", "time": "11:00〜13:00", "status": "〇"},
                        {"label": "D", "time": "10:00〜12:00", "status": "〇"},
                        {"label": "C", "time": "11:00〜13:00", "status": "〇"},
                        {"label": "E", "time": "10:00〜12:00", "status": "〇"},
                    ]
                },
            }
        }
    }

    def get_movie_by_id(movie_id):
        return movie_db.get(movie_id)
    movie = get_movie_by_id(movie_id)
    if movie is None:
        return "映画が見つかりません", 404
    return render_template("movie_information.html", movie=movie)





# guide画面
@app.route('/guide')
def guide():
    return render_template("guide.html")


# seat_reservation画面
@app.route('/seat_reservation/<int:showing_id>', methods=['GET', 'POST'])
def seat_reservation(showing_id):
    accountId = session.get('accountId')

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
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        accountId = request.form.get('accountId')
        accountName = request.form.get('accountName')
        emailAddress = request.form.get('emailAddress')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        realName = request.form.get('realName')
        phoneNumber = request.form.get('phoneNumber')
        birthDate = request.form.get('birthDate')

        if not all([accountId, accountName, emailAddress, password, confirm_password, realName, phoneNumber, birthDate]):
            error = "すべての必須項目を入力してください。"
            return render_template('register.html', error=error)

        if password != confirm_password:
            error = "パスワードが一致しません。"
            return render_template('register.html', error=error)

        if '@' not in emailAddress or '.' not in emailAddress:
            error = "メールアドレスの形式が正しくありません。"
            return render_template('register.html', error=error)

        if not re.match(r"^[0-9\s\+\-]+$", phoneNumber):
            error = "電話番号の形式が正しくありません。"
            return render_template('register.html', error=error)

        hashed_password = generate_password_hash(password)

        conn = conn_db()
        cursor = conn.cursor(buffered=True)
        cursor.execute("SELECT accountId FROM t_account WHERE accountId = %s", (accountId,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            error = "このユーザーIDは既に使用されています。"
            return render_template('register.html', error=error)

        sql = """
            INSERT INTO t_account (
                accountId, accountName, emailAddress, password,
                realName, phoneNumber, birthDate,
                accountIcon, points
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
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
            return redirect('/')
        else:
            error = "メールアドレスまたはパスワードが正しくありません。"
            return render_template('login.html', error=error)

    return render_template('login.html')



# pay画面
@app.route('/pay')
def pay():
    return render_template("pay.html")


# 支払い処理のメインルート（修正版）
@app.route('/process_payment', methods=['POST'])
def process_payment():
    try:
        # セッションからユーザーIDを取得（テスト用に固定値も設定）
        user_id = session.get('user_id', 2)

        if not user_id:
            return jsonify({
                'success': False,
                'message': 'ログインが必要です'
            }), 401

        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'message': 'データが送信されていません'
            }), 400

        payment_method = data.get('payment_method')
        amount = data.get('amount', 1800)  # デフォルト金額

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
                import random
                if random.random() > 0.1:  # 90%の確率で成功
                    payment_status = 'completed'
                    message = 'クレジットカード決済が完了しました'
                else:
                    payment_status = 'failed'
                    message = 'クレジットカード決済に失敗しました'

        elif payment_method == 'convenience':
            phone_number = data.get('phone_number', '')

            if phone_number:
                errors = validate_phone_number(phone_number)

            if not errors:
                payment_number = generate_payment_number()
                payment_data = {
                    'payment_number': payment_number,
                    'phone_number': phone_number[-4:] if len(phone_number) >= 4 else '',  # 下4桁のみ保存
                    'expire_date': (datetime.now().replace(hour=23, minute=59, second=59) +
                                    timedelta(days=3)).isoformat()  # 3日後まで有効
                }
                payment_status = 'pending'
                message = f'コンビニ支払い番号: {payment_number}'

        elif payment_method == 'paypay':
            qr_code = generate_paypay_qr()
            payment_data = {
                'qr_code': qr_code,
                'expire_time': (datetime.now() + timedelta(minutes=15)).isoformat()  # 15分後まで有効
            }
            payment_status = 'pending'
            message = 'PayPayで支払いを完了してください'

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
        payment_id = save_payment_info(user_id, payment_method, payment_data, amount)

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
            'amount': amount
        }

        return jsonify({
            'success': True,
            'message': message,
            'payment_id': payment_id,
            'payment_method': payment_method,
            'status': payment_status,
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
    # セッションから支払い情報を取得
    payment_info = session.get('last_payment')
    print("アクセス")

    if not payment_info:
        # 支払い情報がない場合は支払いページにリダイレクト
        return redirect(url_for('pay'))

    # 支払いステータスが完了なら予約確定処理を実行
    if payment_info.get('status') == 'completed':
        accountId = session.get('accountId')
        seats = session.get('selected_seats', [])
        showing_id = session.get('showing_id')

        if seats and showing_id:
            conn = conn_db()
            cursor = conn.cursor()

            try:
                cursor.execute("SELECT MAX(seatReservationId) FROM t_seatReservation")
                max_id = cursor.fetchone()[0]
                next_id = int(max_id) + 1 if max_id else 1

                for seat in seats:
                    seat_label = f"{seat.get('row')}-{seat.get('seatNumber')}"
                    seatReservationId = f"{next_id:05}"
                    next_id += 1
                    print(f"予約登録: seatReservationId={seatReservationId}, showing_id={showing_id}, accountId={accountId}, seat_label={seat_label}")

                    cursor.execute("""
                        INSERT INTO t_seatReservation (seatReservationId, scheduledShowingId, accountId, seatNumber)
                        VALUES (%s, %s, %s, %s)
                    """, (seatReservationId, showing_id, accountId, seat_label))

                conn.commit()

                # 登録成功したらセッションの座席情報をクリア
                session.pop('selected_seats', None)
                session.pop('showing_id', None)

            except Exception as e:
                conn.rollback()
                print("予約DB登録失敗:", e)
                # ここでエラーメッセージを画面に渡しても良い
                return "予約処理でエラーが発生しました。管理者に連絡してください。", 500

            finally:
                cursor.close()
                conn.close()

    return render_template("pay_comp.html", payment_info=payment_info)



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

        #ID作成
        cur.execute("SELECT MAX(moviesId) FROM t_movies")
        max_id = cur.fetchone()[0]
        if max_id:
            moviesId = f"{int(max_id) + 1:05}"
        else:
            moviesId = "00001"
            

        #入力画面から値の受け取り
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
            INSERT INTO t_movies (
                moviesId,
                movieTitle,
                movieReleaseDate,
                movieEndDate,
                movieRunningTime,
                movieAudienceCount,
                movieSynopsis,
                movieImage
            ) VALUES (
                %(moviesId)s,
                %(movieTitle)s,
                %(movieReleaseDate)s,
                %(movieEndDate)s,
                %(movieRunningTime)s,
                %(movieAudienceCount)s,
                %(movieSynopsis)s,
                %(movieImage)s
            )
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
        
        
    return render_template("add_movie.html")



# add_event画面
@app.route('/add_event', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        con = conn_db()
        cur = con.cursor()

        #ID作成
        cur.execute("SELECT MAX(eventInfoId) FROM t_event")
        max_id = cur.fetchone()[0]
        if max_id:
            eventInfoId = f"{int(max_id) + 1:05}"
        else:
            eventInfoId = "00001"
            

        #入力画面から値の受け取り
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
            INSERT INTO t_event (
                eventInfoId,
                eventTitle,
                eventStartDate,
                eventEndDate,
                eventDescription,
                eventImage,
                eventUrl
            ) VALUES (
                %(eventInfoId)s,
                %(eventTitle)s,
                %(eventStartDate)s,
                %(eventEndDate)s,
                %(eventDescription)s,
                %(eventImage)s,
                %(eventUrl)s
            )
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
        
        
    return render_template("add_event.html")



# add_screening画面
@app.route('/add_screening', methods=['GET', 'POST'])
def add_screening():
    if request.method == 'POST':
        con = conn_db()
        cur = con.cursor()

        #ID作成
        cur.execute("SELECT MAX(scheduledShowingId) FROM t_scheduledShowing")
        max_id = cur.fetchone()[0]
        if max_id:
            scheduledShowingId = f"{int(max_id) + 1:05}"
        else:
            scheduledShowingId = "00001"
            

        #入力画面から値の受け取り
        moviesId = request.form.get('moviesId')
        screenId = request.form.get('screenId')
        scheduledScreeningDate = request.form.get('scheduledScreeningDate')
        screeningStartTime = request.form.get('screeningStartTime')


        errors = {}


        # エラーがある場合はテンプレート再表示
        if errors:
            return render_template('add_event.html', errors=errors)
        
        
        # データの挿入
        sql = """
            INSERT INTO t_scheduledShowing (
                scheduledShowingId,
                moviesId,
                screenId,
                scheduledScreeningDate,
                screeningStartTime
            ) VALUES (
                %(scheduledShowingId)s,
                %(moviesId)s,
                %(screenId)s,
                %(scheduledScreeningDate)s,
                %(screeningStartTime)s
            )
        """
        data = {
            'scheduledShowingId': scheduledShowingId,
            'moviesId': moviesId,
            'screenId': screenId,
            'scheduledScreeningDate': scheduledScreeningDate,
            'screeningStartTime': screeningStartTime
        }
        
        cur.execute(sql, data)
        
        
        con.commit()
        con.close()
        cur.close()
        
        
    # 映画情報の取得（現在上映中 + 近日公開）
    now_playing = fetch_movies(status='now_playing')
    coming_soon = fetch_movies(status='coming_soon')
    movies = now_playing + coming_soon

    # スクリーン情報の取得
    screens = get_screens()
    
        
    return render_template("add_screening.html", movies=movies, screens=screens, movies_json=movies)











#実行制御
if __name__ ==  "__main__":
    app.run(debug=True)