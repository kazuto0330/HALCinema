/**
 * @file profile.js
 * プロフィールページのインタラクションを管理するスクリプト
 */

document.addEventListener('DOMContentLoaded', () => {
    'use strict';

    //================================================================
    // DOM要素の取得
    //================================================================

    // --- プロフィール基本情報関連 ---
    const infoChangeButton = document.getElementById('infoChangeButton');
    const editActions = document.querySelector('.edit-actions');
    const saveButton = document.querySelector('.save-btn');
    const cancelButton = document.querySelector('.cancel-btn');

    const displayElements = {
        nick: document.getElementById('display-nick'),
        name: document.getElementById('display-name'),
        email: document.getElementById('display-email'),
        phone: document.getElementById('display-phone'),
        birth: document.getElementById('display-birth'),
        profileName: document.getElementById('profile-name'),
    };

    const inputElements = {
        nick: document.getElementById('edit-nick'),
        name: document.getElementById('edit-name'),
        email: document.getElementById('edit-email'),
        phone: document.getElementById('edit-phone'),
        birth: document.getElementById('edit-birth'),
    };

    // --- アバター（アイコン）関連 ---
    const avatarPlusButton = document.getElementById('avatar-plus-button');
    const avatarImageInput = document.getElementById('image-input');
    const cropperModal = document.getElementById('cropper-modal');
    const imageToCrop = document.getElementById('image-to-crop');
    const uploadCropButton = document.getElementById('upload-crop-btn');
    const cancelCropButton = document.getElementById('cancel-crop-btn');
    const avatarImage = document.getElementById('avatar-img');
    const headerUserIcon = document.querySelector('header #user-icon'); // ヘッダー内のアイコンを特定

    // --- 購入履歴モーダル関連 ---
    const movieDetailModal = document.getElementById('movie-detail-modal');
    const closeMovieModalButton = document.querySelector('.close-modal-btn');
    const movieCards = document.querySelectorAll('.movie-card');

    // --- 折りたたみセクション関連 ---
    const collapsibleHeader = document.querySelector('.collapsible-header');
    const collapsibleContent = document.querySelector('.collapsible-content');
    const toggleIcon = document.querySelector('.toggle-icon');

    //================================================================
    // 状態管理変数
    //================================================================

    let isEditMode = false;
    let originalProfileValues = {};
    let cropper = null;


    //================================================================
    // プロフィール編集機能
    //================================================================

    /**
     * プロフィール情報の表示/編集モードを切り替える
     */
    const toggleEditMode = () => {
        isEditMode = !isEditMode;
        const allDisplaySpans = document.querySelectorAll('.info-display span');
        const allInputFields = document.querySelectorAll('.info-display input');

        if (isEditMode) {
            // 編集開始時に元の値を保存
            for (const key in inputElements) {
                originalProfileValues[key] = inputElements[key].value;
            }
            // 編集モードへ
            allDisplaySpans.forEach(span => span.style.display = 'none');
            allInputFields.forEach(input => input.style.display = 'block');
            editActions.style.display = 'flex';
        } else {
            // 表示モードへ
            allDisplaySpans.forEach(span => span.style.display = 'inline');
            allInputFields.forEach(input => input.style.display = 'none');
            editActions.style.display = 'none';
        }
    };

    /**
     * プロフィール情報をサーバーに保存する
     */
    const saveProfile = async () => {
        const profileData = {
            accountName: inputElements.nick.value,
            realName: inputElements.name.value,
            emailAddress: inputElements.email.value,
            phoneNumber: inputElements.phone.value,
            birthDate: inputElements.birth.value,
        };

        try {
            const response = await fetch('/add_account', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(profileData),
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.message || `HTTPエラー: ${response.status}`);
            }

            if (result.success) {
                updateProfileDisplays(profileData);
                toggleEditMode();
                showNotification('プロフィールを更新しました', 'success');
            } else {
                throw new Error(result.message || 'サーバー側でエラーが発生しました。');
            }
        } catch (error) {
            console.error('プロフィールの更新に失敗しました:', error);
            showNotification(`更新エラー: ${error.message}`, 'error');
        }
    };

    /**
     * 画面上のプロフィール表示を更新する
     * @param {object} data - 新しいプロフィールデータ
     */
    const updateProfileDisplays = (data) => {
        displayElements.nick.textContent = data.accountName;
        displayElements.profileName.textContent = data.accountName;
        displayElements.name.textContent = data.realName;
        displayElements.email.textContent = data.emailAddress;
        displayElements.phone.textContent = data.phoneNumber;

        const birthDate = new Date(data.birthDate);
        // Invalid Dateでないことを確認
        const formattedBirth = !isNaN(birthDate.getTime())
            ? `${birthDate.getFullYear()}年${String(birthDate.getMonth() + 1).padStart(2, '0')}月${String(birthDate.getDate()).padStart(2, '0')}日`
            : '未設定';
        displayElements.birth.textContent = formattedBirth;
    };

    /**
     * プロフィール編集をキャンセルし、元の値に戻す
     */
    const cancelEdit = () => {
        for (const key in inputElements) {
            inputElements[key].value = originalProfileValues[key];
        }
        toggleEditMode();
    };


    //================================================================
    // アバター（アイコン）変更機能
    //================================================================

    /**
     * Cropperモーダルを開く
     * @param {Event} event - ファイル入力のchangeイベント
     */
    const openCropperModal = (event) => {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            imageToCrop.src = e.target.result;
            cropperModal.style.display = 'flex';

            if (cropper) cropper.destroy();

            cropper = new Cropper(imageToCrop, {
                aspectRatio: 1,
                viewMode: 1,
                dragMode: 'move',
                background: false,
                autoCropArea: 0.8,
            });
        };
        reader.readAsDataURL(file);
        event.target.value = ''; // 同じファイルを選択可能にする
    };
    
    /** Cropperモーダルを閉じる */
    const closeCropperModal = () => {
        cropperModal.style.display = 'none';
        if (cropper) {
            cropper.destroy();
            cropper = null;
        }
    };

    /**
     * CanvasからBlobを非同期で取得するPromiseラッパー
     * @returns {Promise<Blob>}
     */
    const getCanvasBlob = (canvas) => new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.9));

    /**
     * トリミングした画像をアップロードする
     */
    const uploadCroppedImage = async () => {
        if (!cropper) return;

        try {
            const canvas = cropper.getCroppedCanvas({ width: 400, height: 400 });
            const blob = await getCanvasBlob(canvas);
            if (!blob) throw new Error('画像の変換に失敗しました。');

            const formData = new FormData();
            formData.append('croppedImage', blob, 'profile-image.jpg');

            const response = await fetch('/add_account_img', {
                method: 'POST',
                body: formData,
            });
            const result = await response.json();

            if (result.status === 'success') {
                const newImageUrl = `${result.new_icon_url}?t=${new Date().getTime()}`; // キャッシュ対策
                avatarImage.src = newImageUrl;
                if (headerUserIcon) headerUserIcon.src = newImageUrl;
                
                closeCropperModal();
                showNotification('アイコンを更新しました', 'success');
            } else {
                throw new Error(result.message || 'アップロードに失敗しました。');
            }
        } catch (error) {
            console.error('Upload Error:', error);
            showNotification(`アップロードエラー: ${error.message}`, 'error');
        }
    };


    //================================================================
    // 購入履歴モーダル機能
    //================================================================

    //表示切替
    const toggleButton = document.getElementById('point-rank');
    const pointElement = document.getElementById('point');
    const rankElement = document.getElementById('rank');

    //初期表示
    rankElement.classList.toggle('is-hidden');

    toggleButton.addEventListener('click', () => {
        // 3. point要素とrank要素の 'is-hidden' クラスをそれぞれ切り替えます
        pointElement.classList.toggle('is-hidden');
        rankElement.classList.toggle('is-hidden');
    });

    /**
     * 購入履歴カードクリック時にモーダルを表示する
     * @param {Event} event - クリックイベント
     */
    const showMovieDetailModal = (event) => {
        const card = event.currentTarget;
        const {
            movieId, movieTitle, movieImage, screeningDate, screeningTime,
            movieRunningTime, screenId, seatNumber, seatReservationId, movieDescription, amount, createdAt
        } = card.dataset;

        document.getElementById('modal-movie-title').textContent = movieTitle;
        document.getElementById('modal-movie-link').href = `/movie_information/${movieId}`;
        document.getElementById('modal-movie-image').src = movieImage;
        document.getElementById('modal-screening-date').textContent = `上映日: ${screeningDate}`;
        document.getElementById('modal-screening-time').textContent = `上映時間: ${screeningTime} ~ (${movieRunningTime}分)`;
        document.getElementById('modal-seat-info').textContent = `シアター${screenId} (座席: ${seatNumber})`;
        document.getElementById('modal-movie-description').textContent = movieDescription;
        document.getElementById('modal-transaction-id').textContent = `取引ID: ${seatReservationId}`;
        document.getElementById('modal-seat-amount').textContent = `購入価格: ${amount}`;
        document.getElementById('modal-seat-createdAt').textContent = `購入日時: ${createdAt}`;
        movieDetailModal.style.display = 'flex';
    };

    /** 購入履歴モーダルを閉じる */
    const closeMovieModal = () => {
        movieDetailModal.classList.add('closing');
        setTimeout(() => {
            movieDetailModal.style.display = 'none';
            movieDetailModal.classList.remove('closing');
        }, 300); // CSSアニメーションのdurationと合わせる
    };


    //================================================================
    // 折りたたみセクション機能
    //================================================================
    
    /**
     * 基本情報セクションの開閉を制御する
     * @param {Event} event - クリックイベント
     */
    const toggleCollapsibleSection = (event) => {
        if (event.target.closest('#infoChangeButton')) return;

        const isOpen = collapsibleContent.classList.toggle('open');
        toggleIcon.classList.toggle('open');
        infoChangeButton.style.display = isOpen ? 'block' : 'none';

        if (!isOpen && isEditMode) {
            cancelEdit();
        }
    };


    //================================================================
    // 汎用ヘルパー機能
    //================================================================

    /**
     * 画面右上に通知を表示する
     * @param {string} message - 表示するメッセージ
     * @param {'success'|'info'|'error'} type - 通知の種類
     */
    const showNotification = (message, type = 'info') => {
        const notification = document.createElement('div');
        const backgroundColor = {
            success: '#27ae60', info: '#3498db', error: '#e74c3c'
        }[type];

        Object.assign(notification.style, {
            position: 'fixed', top: '20px', right: '20px',
            padding: '15px 20px', backgroundColor, color: 'white',
            borderRadius: '8px', boxShadow: '0 4px 15px rgba(0,0,0,0.2)',
            zIndex: '2000', transform: 'translateX(120%)', opacity: '0',
            transition: 'transform 0.3s ease, opacity 0.3s ease'
        });
        notification.textContent = message;
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
            notification.style.opacity = '1';
        }, 10);

        setTimeout(() => {
            notification.style.transform = 'translateX(120%)';
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    };


    //================================================================
    // イベントリスナーの設定
    //================================================================

    // --- プロフィール編集 ---
    if (infoChangeButton) infoChangeButton.addEventListener('click', toggleEditMode);
    if (saveButton) saveButton.addEventListener('click', saveProfile);
    if (cancelButton) cancelButton.addEventListener('click', cancelEdit);

    // --- アバター変更 ---
    if (avatarPlusButton) avatarPlusButton.addEventListener('click', () => avatarImageInput.click());
    if (avatarImageInput) avatarImageInput.addEventListener('change', openCropperModal);
    if (uploadCropButton) uploadCropButton.addEventListener('click', uploadCroppedImage);
    if (cancelCropButton) cancelCropButton.addEventListener('click', closeCropperModal);
    
    // --- 購入履歴モーダル ---
    movieCards.forEach(card => card.addEventListener('click', showMovieDetailModal));
    if (closeMovieModalButton) closeMovieModalButton.addEventListener('click', closeMovieModal);
    if (movieDetailModal) {
        movieDetailModal.addEventListener('click', (e) => {
            if (e.target === movieDetailModal) closeMovieModal();
        });
    }

    // --- 折りたたみセクション ---
    if (collapsibleHeader) {
        collapsibleHeader.addEventListener('click', toggleCollapsibleSection);
        infoChangeButton.style.display = 'none'; // 初期状態は非表示
    }

    // ページ読み込み時にセッションストレージのキャッシュをクリア
    sessionStorage.removeItem('user_icon_url');
});

// チケットダウンロード
document.querySelectorAll(".movie-card").forEach(card => {
    card.addEventListener("dblclick", () => {
        const reservationId = card.dataset.seatReservationId;
        window.location.href = `/ticket/${reservationId}`;
    });
});
