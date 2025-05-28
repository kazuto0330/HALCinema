const nowBtn = document.getElementById('NowBtn');
const comingBtn = document.getElementById('ComingBtn');
const movieContainer = document.getElementById('MovieContainer');
const tabUnderline = document.getElementById('TabUnderline');

/**
 * アクティブなタブボタンと下線の位置を更新し、コンテンツをスクロールする。
 * @param {HTMLElement} button - クリックされたタブボタン要素。
 * @param {number} targetScrollLeft - MovieContainerの目標スクロール位置。
 */
function setActiveTab(button, targetScrollLeft) {
    // すべてのTabButtonから'active'クラスを削除
    document.querySelectorAll('.TabButton').forEach(btn => {
        btn.classList.remove('active');
    });
    // クリックされたボタンに'active'クラスを追加
    button.classList.add('active');

    // 下線の位置と幅を更新
    tabUnderline.style.left = button.offsetLeft + 'px';
    tabUnderline.style.width = button.offsetWidth + 'px';

    // MovieContainerを即座にスクロール
    movieContainer.scrollLeft = targetScrollLeft;
}

// 初期状態を設定
window.addEventListener('load', () => {
    setActiveTab(nowBtn, 0); // 「上映中」タブをアクティブにし、コンテンツを初期位置に
});

// 上映中ボタンがクリックされた時の処理
nowBtn.addEventListener('click', () => {
    setActiveTab(nowBtn, 0); // 「上映中」タブへ切り替え、コンテンツを左端に
});

// 公開予定ボタンがクリックされた時の処理
comingBtn.addEventListener('click', () => {
    setActiveTab(comingBtn, movieContainer.clientWidth); // 「公開予定」タブへ切り替え、コンテンツを右に
});