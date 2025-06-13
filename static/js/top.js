document.addEventListener('DOMContentLoaded', function () {
    const wrapper = document.querySelector('.slideshow-wrapper');
    const originalSlides = Array.from(wrapper.children);
    const prevButton = document.querySelector('.prev-button');
    const nextButton = document.querySelector('.next-button');

    if (originalSlides.length === 0) return;

    const slideCount = originalSlides.length;
    let currentIndex = 0;
    const ANIMATION_DURATION = 300;
    const SLIDE_INTERVAL = 5000;
    let autoPlayTimer; // タイマーIDを保持する変数

    const lastClone = originalSlides[slideCount - 1].cloneNode(true);
    wrapper.insertBefore(lastClone, originalSlides[0]);
    const firstClone = originalSlides[0].cloneNode(true);
    wrapper.appendChild(firstClone);
    
    const allSlides = document.querySelectorAll('.slide-item');
    const CLONE_COUNT_AHEAD = 1;

    // --- 関数の定義 ---

    function updateSlider(withAnimation = true) {
        if (withAnimation) {
            wrapper.style.transition = `transform ${ANIMATION_DURATION}ms ease-in-out`;
        } else {
            wrapper.style.transition = 'none';
        }

        // ▼▼▼ ここの計算方法を変更 ▼▼▼
        const slideWidth = allSlides[CLONE_COUNT_AHEAD].offsetWidth;
        // 画面全体の幅から現在のスライドの幅を引いて2で割り、正確な中央配置のためのオフセットを計算
        const offset = (window.innerWidth - slideWidth) / 2;
        // ▲▲▲ ここまで変更 ▲▲▲

        const transformValue = -((slideWidth * (currentIndex + CLONE_COUNT_AHEAD))) + offset;
        wrapper.style.transform = `translateX(${transformValue}px)`;

        allSlides.forEach((slide, index) => {
            if (index === currentIndex + CLONE_COUNT_AHEAD) {
                slide.classList.add('active');
            } else {
                slide.classList.remove('active');
            }
        });
    }

    // 次のスライドへ
    function slideToNext() {
        currentIndex++;
        updateSlider();
    }

    // 前のスライドへ
    function slideToPrev() {
        currentIndex--;
        updateSlider();
    }
    
    // 自動再生を開始/リセットする関数
    function startAutoPlay() {
        clearInterval(autoPlayTimer); // 既存のタイマーをクリア
        autoPlayTimer = setInterval(slideToNext, SLIDE_INTERVAL);
    }

    // アニメーション完了時のループ処理
    wrapper.addEventListener('transitionend', () => {
        // 最後のスライド（＝最初の画像のクローン）に到達した場合
        if (currentIndex >= slideCount) {
            currentIndex = 0;
            updateSlider(false);
        }
        // 最初のスライド（=最後の画像のクローン）に到達した場合
        if (currentIndex < 0) {
            currentIndex = slideCount - 1;
            updateSlider(false);
        }
    });

    // --- イベントリスナーの設定 ---

    // 次へボタンがクリックされた時
    nextButton.addEventListener('click', () => {
        slideToNext();
        startAutoPlay(); // タイマーをリセットして再開
    });

    // 前へボタンがクリックされた時
    prevButton.addEventListener('click', () => {
        slideToPrev();
        startAutoPlay(); // タイマーをリセットして再開
    });
    
    // ウィンドウサイズが変更されたとき
    window.addEventListener('resize', () => {
        updateSlider(false);
    });

    // --- 初期化処理 ---
    updateSlider(false);
    startAutoPlay(); // 最初の自動再生を開始
});





// コンテンツスクロールとボタン操作 (ユーザー提供のコードをそのまま残します)
document.addEventListener('DOMContentLoaded', () => {
    const contentContainers = document.querySelectorAll('.ContentContainer');

    contentContainers.forEach(contentContainer => {
        const scrollContainer = contentContainer.querySelector('.ScrollContainer.JsScroll');
        const leftButton = contentContainer.querySelector('.LeftButton');
        const rightButton = contentContainer.querySelector('.RightButton');

        if (scrollContainer && leftButton && rightButton) {
            const scrollAmount = scrollContainer.clientWidth-15;

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
// 定数：ビューポートのはみ出し判定の閾値（左右の余白）
const OUT_OF_BOUNDS_THRESHOLD = 35;

/**
 * 指定された画像要素のビューポート内での位置に基づき、
 * 'darken' クラスを適用または削除する関数。
 * はみ出している場合に 'darken' を適用し、はみ出していない場合に削除します。
 * @param {HTMLElement} img - 処理対象の画像要素（.ContentImg）
 */
function updateImageDarkenState(img) {
    const rect = img.getBoundingClientRect(); // 要素のビューポートに対する位置とサイズを取得
    const viewportWidth = window.innerWidth;
    if (viewportWidth<481){
        return;
    }

    // はみ出し判定
    const isOutOfBounds =
        rect.left < OUT_OF_BOUNDS_THRESHOLD ||             // 左にはみ出し
        rect.right > viewportWidth - OUT_OF_BOUNDS_THRESHOLD; // 右にはみ出し

    // はみ出している場合のみ 'darken' クラスを追加し、CSSでフィルターを適用。
    // はみ出していない場合は 'darken' クラスを削除します (toggleの第二引数がfalseの場合)。
    img.classList.toggle('darken', isOutOfBounds);
}

document.addEventListener('DOMContentLoaded', () => {
    // --- クラス名ScrollContainerの要素にスクロールイベントを追加 ---
    // すべてのScrollContainer要素を取得
    const scrollContainers = document.querySelectorAll('.ScrollContainer');

    if (scrollContainers.length > 0) { // ScrollContainerが存在する場合のみ処理
        scrollContainers.forEach(container => {
            // 各ScrollContainerにスクロールイベントリスナーを追加
            container.addEventListener('scroll', () => {
                // スクロールするたびに、ページ内のすべての.ContentImg要素をチェックし、状態を更新
                const allContentImgs = document.querySelectorAll('.ContentImg');
                allContentImgs.forEach(img => {
                    updateImageDarkenState(img);
                });
            });
        });

        // ページがロードされた初期状態でも一度実行し、画像の状態を正しく反映させる
        // (例: ページリロード時に既にスクロールされている場合など)
        const allContentImgs = document.querySelectorAll('.ContentImg');
        allContentImgs.forEach(img => {
            updateImageDarkenState(img);
        });
    }

    // --- 既存のホバーイベント処理の調整 ---
    const contentContainers = document.querySelectorAll('.ContentContainer');

    contentContainers.forEach(container => {
        const scrollImgs = container.querySelectorAll('.ContentImg');

        // ホバーで実行（マウスが乗った時）
        container.addEventListener('mouseenter', () => {
            scrollImgs.forEach(img => {
                // ホバーしたコンテナ内の画像に対して、はみ出し判定とクラス適用を行う
                updateImageDarkenState(img);
            });
        });

        // ホバー解除で実行（マウスが離れた時）
        container.addEventListener('mouseleave', () => {
            scrollImgs.forEach(img => {
                // ホバー解除時は常に 'darken' クラスを削除し、フィルターをリセット
                // これにより、マウスが離れたら必ずホバーによる効果が消える
                img.classList.remove('darken');
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