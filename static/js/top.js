// スライドショー関連の変数
let slideIndex = 0;
let slides;
let slidesWrapper;
const displayDuration = 6000; // 画像表示時間 (ミリ秒)
let slideTimer;

// CSS設定値 (vw単位) - デフォルト値として扱う
const defaultSlideWidthVw = 65;
const defaultSlideMarginVw = 0.25;

// ページ読み込み後の初期化
document.addEventListener('DOMContentLoaded', () => {
    slides = document.getElementsByClassName("MySlides");
    slidesWrapper = document.querySelector(".SlidesWrapper");

    // 初回スライド表示開始
    showSlides();

    // ウィンドウのリサイズ時にもスライドショーの位置を再計算する
    // これにより、画面サイズ変更時にも正しく中央に表示される
    window.addEventListener('resize', showSlides);
});

// スライド表示とタイマー設定
function showSlides() {
    clearTimeout(slideTimer);

    // レスポンシブ対応: 現在のスライド幅とマージンを決定
    let currentSlideWidthVw;
    let currentSlideMarginVw;

    if (window.innerWidth <= 620) {
        currentSlideWidthVw = 100; // 画面幅いっぱいに
        currentSlideMarginVw = 0;   // マージンなし
    } else {
        currentSlideWidthVw = defaultSlideWidthVw;
        currentSlideMarginVw = defaultSlideMarginVw;
    }

    // インデックス調整 (ループ)
    if (slideIndex >= slides.length) { slideIndex = 0; }
    if (slideIndex < 0) { slideIndex = slides.length - 1; }

    // activeクラスの付け替えと、CSSプロパティの動的設定
    // JavaScriptから直接CSSプロパティを設定することで、メディアクエリと連携しつつ、
    // 正確な計算に基づいたスタイルを適用します。
    for (let i = 0; i < slides.length; i++) {
        slides[i].classList.remove("active");
        // ここでflexとmarginをJavaScriptから設定し、CSSのメディアクエリと連携させる
        slides[i].style.flex = `0 0 ${currentSlideWidthVw}vw`;
        slides[i].style.margin = `0 ${currentSlideMarginVw}vw`;
    }
    slides[slideIndex].classList.add("active");

    // wrapper移動量の計算と適用
    // 計算にはcurrentSlideWidthVwとcurrentSlideMarginVwを使用
    const distanceFromWrapperLeftVw = slideIndex * (currentSlideWidthVw + (2 * currentSlideMarginVw));
    const containerWidthVw = 100; // コンテナ幅 (CSSと合わせる)
    const activeSlideCenterXFromWrapperVw = distanceFromWrapperLeftVw + currentSlideWidthVw / 2;
    const containerCenterXFromWrapperVw = containerWidthVw / 2;
    const moveAmountVw = containerCenterXFromWrapperVw - activeSlideCenterXFromWrapperVw;

    slidesWrapper.style.transform = 'translateX(' + moveAmountVw + 'vw)';

    // 次のスライドへのタイマー再設定
    slideTimer = setTimeout(() => {
        slideIndex++;
        showSlides();
    }, displayDuration);
}

// 前後ボタンでのスライド切り替え
function plusSlides(n) {
    clearTimeout(slideTimer);
    slideIndex += n;
    showSlides();
}

// コンテンツスクロールとボタン操作 (ユーザー提供のコードをそのまま残します)
document.addEventListener('DOMContentLoaded', () => {
    const contentContainers = document.querySelectorAll('.ContentContainer');

    contentContainers.forEach(contentContainer => {
        const scrollContainer = contentContainer.querySelector('.ScrollContainer.JsScroll');
        const leftButton = contentContainer.querySelector('.LeftButton');
        const rightButton = contentContainer.querySelector('.RightButton');

        if (scrollContainer && leftButton && rightButton) {
            const scrollAmount = scrollContainer.clientWidth;

            rightButton.addEventListener('click', () => {
                scrollContainer.scrollBy({ left: scrollAmount, behavior: 'smooth' });
            });

            leftButton.addEventListener('click', () => {
                scrollContainer.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
            });
        }
    });
});


// ボタンのホバー表示/非表示
document.addEventListener('DOMContentLoaded', () => {
    const contentContainers = document.querySelectorAll('.ContentContainer');

    contentContainers.forEach(container => {
        const scrollButtons = container.querySelectorAll('.ScrollButton');

        // 初期非表示
        scrollButtons.forEach(button => {
            button.style.visibility = 'hidden';
        });

        // ホバーで表示
        container.addEventListener('mouseenter', () => {
            scrollButtons.forEach(button => {
                button.style.visibility = 'visible';
            });
        });

        // ホバー解除で非表示
        container.addEventListener('mouseleave', () => {
            scrollButtons.forEach(button => {
                button.style.visibility = 'hidden';
            });
        });
    });
});


// ------------------------公開日付の処理--------------------------------------
document.addEventListener('DOMContentLoaded', () => {
    const targetSelector = '.ImageWrapper a div';
    const yearPattern = /\b20\d{2}年\b/g;
    const breakpoint = 1000;

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