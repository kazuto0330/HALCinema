const nowBtn = document.getElementById('NowBtn');
const comingBtn = document.getElementById('ComingBtn');
const movieContainer = document.getElementById('MovieContainer');
const tabUnderline = document.getElementById('TabUnderline');

/**
 * アクティブなタブボタンと下線の位置を更新し、コンテンツをスクロールする。
 * @param {HTMLElement} button - クリックされたタブボタン要素。
 * @param {number} targetScrollLeft - MovieContainerの目標スクロール位置。
 */
function setActiveTab(button, targetScrollLeft, newUrl) {
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

    //設定されている場合、新しいurlを設定
    if (newUrl){
        history.pushState(null, '', newUrl);
    }
}

// 初期状態を設定
window.addEventListener('load', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const names = urlParams.get('set');
    console.log('set:', names);

    if (names == "comingsoon"){
        setActiveTab(comingBtn, movieContainer.clientWidth);
    }else{
        setActiveTab(nowBtn, 0); // 「上映中」タブをアクティブにし、コンテンツを初期位置に
    }
});

// 上映中ボタンがクリックされた時の処理
nowBtn.addEventListener('click', () => {
    const newUrl = '/movie_list';
    setActiveTab(nowBtn, 0, newUrl); // 「上映中」タブへ切り替え、コンテンツを左端に
});

// 公開予定ボタンがクリックされた時の処理
comingBtn.addEventListener('click', () => {
    const newUrl = '/movie_list?set=comingsoon';
    setActiveTab(comingBtn, movieContainer.clientWidth, newUrl); // 「公開予定」タブへ切り替え、コンテンツを右に
});




// ------------------------公開日付の処理--------------------------------------
document.addEventListener('DOMContentLoaded', () => {
    const targetSelector = '.ComingSoon div';
    const yearPattern = /\b20\d{2}年\b/g;
    const breakpoint = 769;

    function toggleYearDisplay(element, hide) {
        if (!element.dataset.originalHtml) {
            element.dataset.originalHtml = element.innerHTML;
        }
        element.innerHTML = hide ? element.dataset.originalHtml.replace(yearPattern, '') : element.dataset.originalHtml;
    }

    function handleResize() {
        const hideYear = window.innerWidth <= breakpoint;
        document.querySelectorAll(targetSelector).forEach(element => {
            toggleYearDisplay(element, hideYear);
        });
    }

    handleResize();
    window.addEventListener('resize', handleResize);
});