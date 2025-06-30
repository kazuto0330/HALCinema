// ユーザーメニューーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
document.addEventListener('DOMContentLoaded', function() {
    const userIconWrapper = document.getElementById('user-icon-wrapper');

    // アイコンのラッパー要素が存在するかチェック
    if (userIconWrapper) {
        
        // userDataが存在する（ログイン済み）場合
        if (userData) {
            const dropdownMenu = document.getElementById('user-dropdown-menu');
            
            // Tippy.jsのツールチップ内容を更新
            userIconWrapper.setAttribute('data-tippy-content', 'プロフィール');

            if (dropdownMenu) {
                // アイコンをクリックしたときの処理（メニュー表示/非表示）
                userIconWrapper.addEventListener('click', function(event) {
                    event.stopPropagation(); // 親要素へのイベント伝播を停止
                    dropdownMenu.classList.toggle('show');
                });

                // メニュー自身をクリックしても閉じないようにする
                dropdownMenu.addEventListener('click', function(event) {
                    event.stopPropagation();
                });
            }

            // ドキュメント全体をクリックしたらメニューを閉じる
            window.addEventListener('click', function() {
                if (dropdownMenu && dropdownMenu.classList.contains('show')) {
                    dropdownMenu.classList.remove('show');
                }
            });
        } 
        // userDataがnull（未ログイン）の場合
        else {
            // Tippy.jsのツールチップ内容を「ログイン」に変更（親切設計）
            userIconWrapper.setAttribute('data-tippy-content', 'ログイン');

            // アイコンをクリックしたらログインページにリダイレクト
            userIconWrapper.addEventListener('click', function() {
                window.location.href = '/login';
            });
        }
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