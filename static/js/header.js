// DOMが完全に読み込まれたら処理を開始
document.addEventListener('DOMContentLoaded', async () => {
    const userIconElement = document.getElementById('user-icon');
    if (!userIconElement) return;

    // キャッシュを保存するためのキーを定義
    const CACHE_KEY = 'user_icon_url';

    // 1. sessionStorageからキャッシュを確認
    const cachedIconUrl = sessionStorage.getItem(CACHE_KEY);

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

        // データとaccountIconプロパティが存在することを確認
        if (data && data.accountIcon) {
            const iconUrl = `/static/images/usericon/80x80/${data.accountIcon}`;

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
    }
});