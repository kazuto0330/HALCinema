// スライドショー関連の変数
let slideIndex = 0;
let slides;
let slidesWrapper;
const displayDuration = 6000; // 画像表示時間 (ミリ秒)
let slideTimer;

// CSS設定値 (vw単位)
const slideWidthVw = 65;
const slideMarginVw = 0.25;

// ページ読み込み後の初期化
document.addEventListener('DOMContentLoaded', () => {
    slides = document.getElementsByClassName("mySlides");
    slidesWrapper = document.querySelector(".slides-wrapper");

    // 初回スライド表示開始
    showSlides();
});

// スライド表示とタイマー設定
function showSlides() {
    clearTimeout(slideTimer);

    // インデックス調整 (ループ)
    if (slideIndex >= slides.length) { slideIndex = 0; }
    if (slideIndex < 0) { slideIndex = slides.length - 1; }

    // activeクラスの付け替え
    for (let i = 0; i < slides.length; i++) {
        slides[i].classList.remove("active");
    }
    slides[slideIndex].classList.add("active");

    // wrapper移動量の計算と適用
    const distanceFromWrapperLeftVw = slideIndex * (slideWidthVw + 2 * slideMarginVw);
    const containerWidthVw = 100; // コンテナ幅 (CSSと合わせる)
    const activeSlideCenterXFromWrapperVw = distanceFromWrapperLeftVw + slideWidthVw / 2;
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

// コンテンツスクロールとボタン操作
document.addEventListener('DOMContentLoaded', () => {
    const ContentContainers = document.querySelectorAll('.ContentContainer');

    ContentContainers.forEach(ContentContainer => {
        const ScrollContainer = ContentContainer.querySelector('.ScrollContainer.JsScroll');
        const LeftButton = ContentContainer.querySelector('.LeftButton');
        const RightButton = ContentContainer.querySelector('.RightButton');

        if (ScrollContainer && LeftButton && RightButton) {
            const ScrollAmount = ScrollContainer.clientWidth;

            RightButton.addEventListener('click', () => {
                ScrollContainer.scrollBy({ left: ScrollAmount, behavior: 'smooth' });
            });

            LeftButton.addEventListener('click', () => {
                ScrollContainer.scrollBy({ left: -ScrollAmount, behavior: 'smooth' });
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