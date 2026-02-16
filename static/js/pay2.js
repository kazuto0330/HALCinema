// 支払い方法選択のイベントリスナー
document.addEventListener('DOMContentLoaded', function() {
    const paymentOptions = document.querySelectorAll('.payment-option');
    
    paymentOptions.forEach(option => {
        option.addEventListener('click', function() {
            const method = this.getAttribute('data-method');
            handlePaymentSelection(method);
        });
        
        // アクセシビリティ向上のためキーボード操作対応
        option.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                const method = this.getAttribute('data-method');
                handlePaymentSelection(method);
            }
        });
        
        // タブキー対応
        option.setAttribute('tabindex', '0');
    });
});

// 支払い方法選択時の処理
function handlePaymentSelection(method) {
    let methodName = '';
    
    switch(method) {
        case 'cash':
            methodName = '現金';
            break;
        case 'credit':
            methodName = 'クレジットカード';
            break;
        case 'qr':
            methodName = 'コード決済';
            break;
        default:
            methodName = '不明な支払い方法';
    }
    
    // 選択された支払い方法をコンソールに出力（デバッグ用）
    console.log('選択された支払い方法:', methodName);
    
    // 選択フィードバック
    showSelectionFeedback(event.currentTarget);
    
    // 実際の処理はここに追加
    // 例: 次の画面に遷移、APIリクエスト送信など
    setTimeout(() => {
        // alert(`${methodName}を選択しました`);
        // ここで次のページへの遷移やフォーム送信を行う
        // window.location.href = `/payment/${method}`;
    }, 300);
}

// 選択時のビジュアルフィードバック
function showSelectionFeedback(element) {
    // 全ての選択肢からアクティブクラスを削除
    document.querySelectorAll('.payment-option').forEach(opt => {
        opt.style.borderColor = '#e0e0e0';
    });
    
    // 選択された要素にアクティブスタイルを適用
    element.style.borderColor = '#2196F3';
    
    // アニメーション効果
    element.style.transform = 'scale(0.98)';
    setTimeout(() => {
        element.style.transform = 'scale(1)';
    }, 100);
}

// データの動的読み込み（オプション）
// 予約情報をサーバーから取得する場合の例
function loadReservationData(reservationId) {
    // APIから予約情報を取得
    // fetch(`/api/reservation/${reservationId}`)
    //     .then(response => response.json())
    //     .then(data => {
    //         updateReservationCard(data);
    //     })
    //     .catch(error => {
    //         console.error('予約情報の取得に失敗しました:', error);
    //     });
}

// 予約情報カードの更新（オプション）
function updateReservationCard(data) {
    // データを基にカードの内容を更新
    document.querySelector('.movie-title').textContent = data.movieTitle;
    // 他の要素も同様に更新...
}

// ページ読み込み時に予約IDがある場合は情報を取得
// const urlParams = new URLSearchParams(window.location.search);
// const reservationId = urlParams.get('id');
// if (reservationId) {
//     loadReservationData(reservationId);
// }