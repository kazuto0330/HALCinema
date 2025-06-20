// DOMが完全に読み込まれたら処理を開始
document.addEventListener('DOMContentLoaded', async () => {
    const userIconElement = document.getElementById('user-icon');
    if (!userIconElement) return;

    // キャッシュを保存するためのキーを定義
    const CACHE_KEY = 'user_icon_url';

    
    // 1. sessionStorageからキャッシュを確認
    const cachedIconUrl = sessionStorage.getItem(CACHE_KEY);
    console.log(cachedIconUrl);

    // 2. キャッシュがあれば、それを使って処理を終了
    if (cachedIconUrl) {
        console.log('キャッシュからアイコンを読み込みました。');
        userIconElement.src = cachedIconUrl;
        return; // APIリクエストは不要なのでここで終了
    }
    

    try {
        // APIにGETリクエストを送信
        const response = await fetch('/api/user_icon');

        // レスポンスが正常でない場合 (例: 404, 500エラー)
        if (!response.ok) {
            throw new Error(`APIエラー: ${response.status}`);
        }

        // レスポンスのJSONをパース
        const data = await response.json();

        // データの構造を確認（新しいAPIレスポンス形式に対応）
        const iconFileName = data.success ? data.accountIcon : (data.accountIcon || null);

        // データとaccountIconプロパティが存在することを確認
        if (iconFileName) {
            const iconUrl = `/static/images/usericon/80x80/${iconFileName}`;

            sessionStorage.setItem(CACHE_KEY, iconUrl);
            console.log('アイコンURLをキャッシュに保存しました。');

            // <img>要素のsrc属性を更新して画像を表示
            userIconElement.src = iconUrl;
        } else {
            console.warn('APIから有効なアイコンパスが取得できませんでした。');
            userIconElement.src = '/static/images/usericon/80x80/default.jpg';
        }

    } catch (error) {
        // ネットワークエラーやJSONパースエラーなどをキャッチ
        console.error('アイコンの取得に失敗しました:', error);
        // エラー時もデフォルト画像を表示
        userIconElement.src = '/static/images/usericon/80x80/default.jpg';
    }
});


// スマホ用ハンバーガーメニューーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー

// DOMが読み込まれたら実行
document.addEventListener('DOMContentLoaded', () => {
    // 必要な要素を取得
    const hamburgerIcon = document.getElementById('hamburger-icon');
    const bentoIcon = document.getElementById('bento-menu-icon');
    const navMenu = document.getElementById('nav-menu');
    const closeButton = document.getElementById('close-button');
    const menuOverlay = document.getElementById('menu-overlay');

    // メニューを開く関数
    const openMenu = () => {
        navMenu.classList.add('is-active');
        menuOverlay.classList.add('is-active');
    };

    // メニューを閉じる関数
    const closeMenu = () => {
        navMenu.classList.remove('is-active');
        menuOverlay.classList.remove('is-active');
    };

    // ハンバーガーアイコンがクリックされたらメニューを開く
    hamburgerIcon.addEventListener('click', openMenu);
    // 弁当メニュー 〃
    bentoIcon.addEventListener('click', openMenu);

    // 閉じるボタンがクリックされたらメニューを閉じる
    closeButton.addEventListener('click', closeMenu);

    // オーバーレイがクリックされたらメニューを閉じる
    menuOverlay.addEventListener('click', closeMenu);
});