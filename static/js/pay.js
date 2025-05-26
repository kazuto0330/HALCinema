document.addEventListener('DOMContentLoaded', function() {
    // 支払い方法の切り替え
    const paymentMethods = document.querySelectorAll('input[name="payment-method"]');

    paymentMethods.forEach(method => {
        method.addEventListener('change', function() {
            // すべての詳細を非表示
            document.querySelectorAll('.method-details').forEach(detail => {
                detail.style.display = 'none';
            });

            // 選択された支払い方法の詳細を表示
            const detailsId = this.id + '-details';
            document.getElementById(detailsId).style.display = 'block';
        });
    });

    // 初期状態でクレジットカードの詳細を表示
    document.getElementById('credit-card-details').style.display = 'block';

    // カード番号のフォーマット
    const cardNumber = document.getElementById('card-number');
    cardNumber.addEventListener('input', function(e) {
        let value = e.target.value.replace(/\s+/g, '').replace(/[^0-9]/g, '');
        if (value.length > 0) {
            value = value.match(new RegExp('.{1,4}', 'g')).join(' ');
        }
        e.target.value = value;
    });

    // 有効期限のフォーマット
    const expiryDate = document.getElementById('expiry-date');
    expiryDate.addEventListener('input', function(e) {
        let value = e.target.value.replace(/\D/g, '');
        if (value.length >= 2) {
            value = value.substring(0, 2) + '/' + value.substring(2, 4);
        }
        e.target.value = value;
    });

    // セキュリティコードの数字のみ許可
    const securityCode = document.getElementById('security-code');
    securityCode.addEventListener('input', function(e) {
        e.target.value = e.target.value.replace(/\D/g, '');
    });

    // フォーム送信処理
    const paymentForm = document.getElementById('payment-form');
    paymentForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const selectedMethod = document.querySelector('input[name="payment-method"]:checked').value;

        if (selectedMethod === 'credit-card') {
            // クレジットカード情報のバリデーション
            if (!validateCreditCard()) {
                return;
            }
        }

        // ここで実際の送信処理を行う
        alert('支払い方法: ' + getPaymentMethodName(selectedMethod) + '\n処理を続行します...');
        // paymentForm.submit(); // 実際の送信を行う場合はこちらを使用
    });

    function validateCreditCard() {
        const cardNumber = document.getElementById('card-number').value.replace(/\s/g, '');
        const expiryDate = document.getElementById('expiry-date').value;
        const securityCode = document.getElementById('security-code').value;
        const cardName = document.getElementById('card-name').value.trim();

        if (cardNumber.length !== 16) {
            alert('カード番号が正しくありません。16桁の番号を入力してください。');
            return false;
        }

        if (!expiryDate.match(/^\d{2}\/\d{2}$/)) {
            alert('有効期限が正しくありません。MM/YY形式で入力してください。');
            return false;
        }

        if (securityCode.length < 3) {
            alert('セキュリティコードが正しくありません。3桁の番号を入力してください。');
            return false;
        }

        if (cardName === '') {
            alert('カード名義を入力してください。');
            return false;
        }

        return true;
    }

    function getPaymentMethodName(methodValue) {
        switch(methodValue) {
            case 'credit-card': return 'クレジットカード';
            case 'convenience': return 'コンビニ払い';
            case 'paypay': return 'PayPay';
            default: return '不明な支払い方法';
        }
    }
});