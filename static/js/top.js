// =============================================================================
// 機能定義エリア
// 各機能の初期化関数をここで定義します。
// =============================================================================

/**
 * 1. スライドショー機能
 * 無限ループのスライドショーを初期化します。
 */
function initSlideshow() {
    const wrapper = document.querySelector('.slideshow-wrapper');
    // スライドショーの要素がなければ処理を中断
    if (!wrapper) return;

    const originalSlides = Array.from(wrapper.children);
    const prevButton = document.querySelector('.prev-button');
    const nextButton = document.querySelector('.next-button');

    // 必要な要素が揃っていない場合は処理を中断
    if (originalSlides.length === 0 || !prevButton || !nextButton) return;

    const slideCount = originalSlides.length;
    let currentIndex = 0;
    const ANIMATION_DURATION = 300;
    const SLIDE_INTERVAL = 4000;
    let autoPlayTimer;

    // 無限ループのためのクローンを生成・配置
    const lastClone = originalSlides[slideCount - 1].cloneNode(true);
    wrapper.insertBefore(lastClone, originalSlides[0]);
    const firstClone = originalSlides[0].cloneNode(true);
    wrapper.appendChild(firstClone);
    
    const allSlides = document.querySelectorAll('.slide-item');
    const CLONE_COUNT_AHEAD = 1; // 先頭に追加したクローンの数

    // スライドの位置とアクティブ状態を更新する関数
    function updateSlider(withAnimation = true) {
        wrapper.style.transition = withAnimation ? `transform ${ANIMATION_DURATION}ms ease-in-out` : 'none';

        const slideWidth = allSlides[CLONE_COUNT_AHEAD].offsetWidth;
        // スライドを画面中央に配置するためのオフセットを計算
        const offset = (window.innerWidth - slideWidth) / 2;
        const transformValue = -((slideWidth * (currentIndex + CLONE_COUNT_AHEAD))) + offset;
        wrapper.style.transform = `translateX(${transformValue}px)`;

        // アクティブなスライドに 'active' クラスを付与
        allSlides.forEach((slide, index) => {
            slide.classList.toggle('active', index === currentIndex + CLONE_COUNT_AHEAD);
        });
    }

    // 次のスライドへ移動
    const slideToNext = () => {
        currentIndex++;
        updateSlider();
    };

    // 前のスライドへ移動
    const slideToPrev = () => {
        currentIndex--;
        updateSlider();
    };
    
    // 自動再生を開始またはリセット
    const startAutoPlay = () => {
        clearInterval(autoPlayTimer);
        autoPlayTimer = setInterval(slideToNext, SLIDE_INTERVAL);
    };

    // アニメーション完了後のループ処理
    wrapper.addEventListener('transitionend', () => {
        if (currentIndex >= slideCount) {
            currentIndex = 0;
            updateSlider(false); // アニメーションなしで最初のスライドに移動
        }
        if (currentIndex < 0) {
            currentIndex = slideCount - 1;
            updateSlider(false); // アニメーションなしで最後のスライドに移動
        }
    });

    // ボタンのクリックイベント
    nextButton.addEventListener('click', () => {
        slideToNext();
        startAutoPlay();
    });

    prevButton.addEventListener('click', () => {
        slideToPrev();
        startAutoPlay();
    });
    
    // ウィンドウリサイズ時に位置を再計算
    window.addEventListener('resize', () => updateSlider(false));

    // 初期化
    updateSlider(false);
    startAutoPlay();
}

/**
 * 2. コンテンツスクローラー機能
 * ボタンによるスクロールと、画像のダークン効果を初期化します。
 */
function initContentScrollers() {
    const contentContainers = document.querySelectorAll('.ContentContainer');
    if (contentContainers.length === 0) return;

    // --- 定数定義 ---
    const OUT_OF_BOUNDS_THRESHOLD = 35; // はみ出し判定の閾値 (px)
    const MOBILE_BREAKPOINT = 481;      // ダークン効果を無効にする画面幅 (px)
    const SCROLL_OFFSET = 15;           // ボタンクリック時のスクロール量の調整値 (px)

    /**
     * 画像がビューポートの端からはみ出しているか判定し、'darken'クラスを適用/削除する
     * @param {HTMLElement} img - 対象の画像要素 (.ContentImg)
     */
    function updateImageDarkenState(img) {
        if (window.innerWidth < MOBILE_BREAKPOINT) {
            img.classList.remove('darken');
            return;
        }
        const rect = img.getBoundingClientRect();
        const viewportWidth = window.innerWidth;
        const isOutOfBounds = rect.left < OUT_OF_BOUNDS_THRESHOLD || rect.right > viewportWidth - OUT_OF_BOUNDS_THRESHOLD;
        img.classList.toggle('darken', isOutOfBounds);
    }

    // --- 各コンテナにイベントを設定 ---
    contentContainers.forEach(container => {
        const scrollContainer = container.querySelector('.ScrollContainer.JsScroll');
        const leftButton = container.querySelector('.LeftButton');
        const rightButton = container.querySelector('.RightButton');
        const scrollImgs = container.querySelectorAll('.ContentImg');

        // a) スクロールボタンの操作
        if (scrollContainer && leftButton && rightButton) {
            const scrollAmount = () => scrollContainer.clientWidth - SCROLL_OFFSET;
            rightButton.addEventListener('click', () => {
                scrollContainer.scrollBy({ left: scrollAmount(), behavior: 'smooth' });
            });
            leftButton.addEventListener('click', () => {
                scrollContainer.scrollBy({ left: -scrollAmount(), behavior: 'smooth' });
            });
        }

        // b) 画像のダークン効果
        if (scrollContainer && scrollImgs.length > 0) {
            // スクロール時にコンテナ内の画像を更新
            scrollContainer.addEventListener('scroll', () => {
                scrollImgs.forEach(updateImageDarkenState);
            });
        }
        // ホバー時にコンテナ内の画像を更新
        container.addEventListener('mouseenter', () => {
            scrollImgs.forEach(updateImageDarkenState);
        });
        // ホバー解除時はダークン効果をすべて解除
        container.addEventListener('mouseleave', () => {
            scrollImgs.forEach(img => img.classList.remove('darken'));
        });
    });

    // --- ページ全体に適用するイベント ---
    const updateAllImagesOnPage = () => {
        document.querySelectorAll('.ContentImg').forEach(updateImageDarkenState);
    };
    
    // リサイズ時に全画像の表示を更新
    window.addEventListener('resize', updateAllImagesOnPage);
    // 初期ロード時にも実行して現在の状態を反映
    updateAllImagesOnPage();
}

/**
 * 3. 公開日付のレスポンシブ表示機能
 * 画面幅に応じて日付の「年」の表示/非表示を切り替えます。
 */
function initDateDisplay() {
    const TARGET_SELECTOR = '.ImageWrapper a div';
    const dateElements = document.querySelectorAll(TARGET_SELECTOR);
    if (dateElements.length === 0) return;

    const YEAR_PATTERN = /\b20\d{2}年\b/g; // "20xx年" の形式にマッチ
    const BREAKPOINT = 1000; // 年表示を切り替える画面幅 (px)

    /**
     * 要素のinnerHTMLから年表示を削除または復元する
     * @param {HTMLElement} element - 対象の要素
     * @param {boolean} hide - trueなら年を隠し、falseなら表示する
     */
    function toggleYearDisplay(element, hide) {
        // 元のHTMLを初回のみdatasetに保存
        if (!element.dataset.originalHtml) {
            element.dataset.originalHtml = element.innerHTML;
        }
        // 画面幅に応じて年を削除、または元のHTMLに戻す
        element.innerHTML = hide ? element.dataset.originalHtml.replace(YEAR_PATTERN, '') : element.dataset.originalHtml;
    }

    // 表示を更新するメインの関数
    function handleResize() {
        const shouldHideYear = window.innerWidth <= BREAKPOINT;
        dateElements.forEach(element => toggleYearDisplay(element, shouldHideYear));
    }

    // 初期表示とリサイズ時に実行
    handleResize();
    window.addEventListener('resize', handleResize);
}


// =============================================================================
// イベントリスナー登録エリア
// ページの読み込み完了時に、定義済みの各機能を初期化します。
// =============================================================================
document.addEventListener('DOMContentLoaded', () => {
    initSlideshow();
    initContentScrollers();
    initDateDisplay();
});