/* pay_comp.js - 強化版 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('支払い完了ページが読み込まれました');

    // ページ読み込み時にセッションストレージから支払い結果を取得
    const paymentResult = sessionStorage.getItem('paymentResult');
    if (paymentResult) {
        try {
            const result = JSON.parse(paymentResult);
            console.log('セッションから取得した支払い結果:', result);

            // 必要に応じて追加の処理を実行
            if (result.success && result.payment_method === 'convenience') {
                // コンビニ払いの場合の特別な処理
                showConvenienceInstructions(result);
            } else if (result.success && result.payment_method === 'paypay') {
                // PayPayの場合の特別な処理
                showPayPayInstructions(result);
            }

        } catch (e) {
            console.error('支払い結果の解析に失敗:', e);
        }

        // 使用済みの情報をクリア
        sessionStorage.removeItem('paymentResult');
    }

    // コンプリートボタンのイベント処理
    const completeButtons = document.querySelectorAll('.complete-button');
    completeButtons.forEach(button => {
        button.addEventListener('click', handleComplete);
    });

    // エラー情報がある場合のログ出力
    const errorMessage = document.querySelector('.error-message');
    if (errorMessage) {
        console.error('支払い完了ページでエラー:', errorMessage.textContent);
    }

    // 成功時のアニメーション効果
    const checkIcon = document.querySelector('.check-icon');
    if (checkIcon && !checkIcon.classList.contains('error-icon') && !checkIcon.classList.contains('warning-icon')) {
        // 成功アイコンにパルス効果を追加
        setTimeout(() => {
            checkIcon.style.animation = 'checkPop 0.8s ease-out, pulse 2s infinite 1s';
        }, 800);
    }

    // 支払い詳細情報の表示アニメーション
    animatePaymentDetails();
});

function handleComplete(event) {
    console.log('完了ボタンがクリックされました');

    // ローカルストレージの支払い関連情報をクリア
    try {
        localStorage.removeItem('payment_data');
        localStorage.removeItem('selected_seats');
        localStorage.removeItem('showing_id');
        sessionStorage.removeItem('paymentResult');
        console.log('ストレージの情報をクリアしました');
    } catch (e) {
        console.warn('ストレージのクリアに失敗:', e);
    }

    // アニメーション効果を追加してからページ遷移
    const button = event.target;
    button.style.transform = 'scale(0.95)';
    button.style.transition = 'transform 0.15s ease';

    setTimeout(() => {
        button.style.transform = 'scale(1)';
    }, 150);
}

function showConvenienceInstructions(result) {
    console.log('コンビニ払いの案内を表示');

    // コンビニ払いの詳細案内を動的に追加
    const container = document.querySelector('.container');
    const instructionsDiv = document.createElement('div');
    instructionsDiv.className = 'instructions-container';

    // 期限日の計算
    let expireDate = '3日後';
    if (result.data && result.data.expire_date) {
        try {
            const expire = new Date(result.data.expire_date);
            expireDate = expire.toLocaleDateString('ja-JP', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        } catch (e) {
            console.warn('期限日の解析に失敗:', e);
        }
    }

    instructionsDiv.innerHTML = `
        <div class="instructions-title">
            📋 コンビニでのお支払い手順
        </div>
        <div class="instructions-content">
            <strong>1. 支払い番号の確認</strong><br>
            上記の支払い番号をメモまたはスクリーンショットで保存してください。<br><br>
            
            <strong>2. コンビニエンスストアへ</strong><br>
            お近くのコンビニエンスストア（セブン-イレブン、ローソン、ファミリーマートなど）へお越しください。<br><br>
            
            <strong>3. レジでお支払い</strong><br>
            レジで「料金収納代行」または「各種料金お支払い」とお伝えし、支払い番号を提示してください。<br><br>
            
            <strong>4. お支払い完了</strong><br>
            料金をお支払いいただき、レシートを受け取って完了です。<br><br>
            
            <small style="color: #e74c3c;">
                ⚠️ <strong>お支払い期限:</strong> ${expireDate}<br>
                期限を過ぎると支払い番号が無効になりますのでご注意ください。
            </small>
        </div>
    `;

    const completeButton = container.querySelector('.complete-button');
    container.insertBefore(instructionsDiv, completeButton);

    // アニメーション効果
    instructionsDiv.style.opacity = '0';
    instructionsDiv.style.transform = 'translateY(20px)';
    instructionsDiv.style.transition = 'all 0.5s ease';

    setTimeout(() => {
        instructionsDiv.style.opacity = '1';
        instructionsDiv.style.transform = 'translateY(0)';
    }, 100);
}

function showPayPayInstructions(result) {
    console.log('PayPay決済の案内を表示');

    // PayPayの詳細案内を動的に追加
    const container = document.querySelector('.container');
    const instructionsDiv = document.createElement('div');
    instructionsDiv.className = 'instructions-container';

    instructionsDiv.innerHTML = `
        <div class="instructions-title">
            📱 PayPay決済完了のご案内
        </div>
        <div class="instructions-content">
            <strong>✅ 決済が正常に完了しました</strong><br><br>
            
            PayPayアプリでの決済が正常に処理されました。<br>
            決済履歴や詳細はPayPayアプリからご確認いただけます。<br><br>
            
            <strong>📋 確認方法</strong><br>
            1. PayPayアプリを開く<br>
            2. 「取引履歴」をタップ<br>
            3. 今回の決済内容を確認<br><br>
            
            <small style="color: #2196f3;">
                💡 領収書が必要な場合は、PayPayアプリの取引履歴から印刷・保存が可能です。
            </small>
        </div>
    `;

    const completeButton = container.querySelector('.complete-button');
    container.insertBefore(instructionsDiv, completeButton);

    // アニメーション効果
    instructionsDiv.style.opacity = '0';
    instructionsDiv.style.transform = 'translateY(20px)';
    instructionsDiv.style.transition = 'all 0.5s ease';

    setTimeout(() => {
        instructionsDiv.style.opacity = '1';
        instructionsDiv.style.transform = 'translateY(0)';
    }, 100);
}

function animatePaymentDetails() {
    // 支払い詳細の要素を順次アニメーション表示
    const detailElements = document.querySelectorAll('.payment-details, .seats-info');

    detailElements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = 'all 0.4s ease';

        setTimeout(() => {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, 300 + (index * 150));
    });
}

// エラーハンドリング
window.addEventListener('error', function(e) {
    console.error('JavaScriptエラーが発生しました:', e.error);
});

// ページを離れる前の処理
window.addEventListener('beforeunload', function(e) {
    // 重要な情報のクリーンアップ
    try {
        sessionStorage.removeItem('paymentResult');
    } catch (error) {
        console.warn('セッションストレージのクリアに失敗:', error);
    }
});