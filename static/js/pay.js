document.addEventListener('DOMContentLoaded', function() {
    console.log('pay.js loaded');

    // DOM要素の取得
    const paymentForm = document.getElementById('payment-form');
    const paymentMethods = document.querySelectorAll('input[name="payment-method"]');
    const submitButton = document.getElementById('submit-payment');
    const loadingOverlay = document.getElementById('loading-overlay');
    const generalErrorsDiv = document.getElementById('general-errors');

    // 支払い方法の切り替え処理
    paymentMethods.forEach(method => {
        method.addEventListener('change', function() {
            // すべての詳細セクションを非表示
            document.querySelectorAll('.method-details').forEach(detail => {
                detail.style.display = 'none';
            });

            // すべての支払い方法のスタイルをリセット
            document.querySelectorAll('.payment-method').forEach(pm => {
                pm.classList.remove('selected');
            });

            // 選択された支払い方法の詳細を表示
            const detailsId = this.id + '-details';
            const detailsElement = document.getElementById(detailsId);
            if (detailsElement) {
                detailsElement.style.display = 'block';
            }

            // 選択された支払い方法にスタイルを適用
            this.closest('.payment-method').classList.add('selected');

            // エラーメッセージをクリア
            clearAllErrors();
        });
    });

    // 初期状態の設定
    document.getElementById('credit-card-details').style.display = 'block';
    document.querySelector('.payment-method').classList.add('selected');

    // カード番号のフォーマット処理
    const cardNumberInput = document.getElementById('card-number');
    if (cardNumberInput) {
        cardNumberInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\s+/g, '').replace(/[^0-9]/g, '');
            if (value.length > 16) {
                value = value.substring(0, 16);
            }
            if (value.length > 0) {
                value = value.match(/.{1,4}/g).join(' ');
            }
            e.target.value = value;

            // リアルタイムバリデーション
            if (value.replace(/\s/g, '').length > 0) {
                validateCardNumber(value.replace(/\s/g, ''));
            }
        });
    }

    // 有効期限のフォーマット処理（完全リセット版）
    const originalExpiryInput = document.getElementById('expiry-date');
    if (originalExpiryInput) {
        console.log('有効期限フィールドを初期化中...');

        // 完全に新しい要素を作成
        const newExpiryInput = document.createElement('input');
        newExpiryInput.type = 'text';
        newExpiryInput.id = 'expiry-date';
        newExpiryInput.placeholder = 'MM/YY';
        newExpiryInput.maxLength = '5';
        newExpiryInput.required = true;

        // 元の要素のスタイルをコピー
        newExpiryInput.className = originalExpiryInput.className;

        // 親要素から元の要素を削除し、新しい要素を追加
        const parent = originalExpiryInput.parentNode;
        parent.removeChild(originalExpiryInput);
        parent.insertBefore(newExpiryInput, parent.querySelector('.error-message'));

        console.log('新しい有効期限フィールドを作成');

        // 入力イベント
        newExpiryInput.addEventListener('input', function(e) {
            console.log('=== INPUT EVENT ===');
            console.log('元の値:', e.target.value);

            // 数字のみ抽出
            let value = e.target.value.replace(/\D/g, '');
            console.log('数字のみ:', value);

            // 4桁制限
            if (value.length > 4) {
                value = value.substring(0, 4);
                console.log('4桁制限後:', value);
            }

            // フォーマット
            if (value.length >= 3) {
                value = value.substring(0, 2) + '/' + value.substring(2);
                console.log('フォーマット後:', value);
            }

            // 値を設定
            e.target.value = value;
            console.log('最終値:', e.target.value);

            // バリデーション
            if (value.length === 5) {
                validateExpiryDate(value);
            } else {
                clearError('expiry-date-error');
            }
            console.log('===================');
        });

        // キーダウンイベント
        newExpiryInput.addEventListener('keydown', function(e) {
            console.log('=== KEYDOWN EVENT ===');
            console.log('押されたキー:', e.key);
            console.log('カーソル位置:', e.target.selectionStart);
            console.log('現在の値:', e.target.value);

            if (e.key === 'Backspace') {
                const pos = e.target.selectionStart;
                const value = e.target.value;

                console.log('バックスペース検出');
                console.log('位置:', pos, '値:', value);

                // スラッシュの直後（位置3）でバックスペース
                if (pos === 3 && value.charAt(2) === '/') {
                    console.log('スラッシュ位置でのバックスペース検出');
                    e.preventDefault();

                    // 月の部分の最後の桁を削除
                    const monthPart = value.substring(0, 2);
                    if (monthPart.length > 0) {
                        const newValue = monthPart.substring(0, monthPart.length - 1);
                        console.log('新しい値:', newValue);

                        e.target.value = newValue;

                        // カーソル位置を設定
                        setTimeout(() => {
                            e.target.setSelectionRange(newValue.length, newValue.length);
                            console.log('カーソル位置設定:', newValue.length);
                        }, 0);
                    }
                }
            }

            // 数字以外の入力を防ぐ
            if (!/\d/.test(e.key) &&
                !['Backspace', 'Delete', 'Tab', 'Enter', 'ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(e.key) &&
                !e.ctrlKey && !e.metaKey) {
                console.log('無効なキーをブロック:', e.key);
                e.preventDefault();
            }
            console.log('====================');
        });

        // ペースト処理
        newExpiryInput.addEventListener('paste', function(e) {
            e.preventDefault();

            const pastedData = (e.clipboardData || window.clipboardData).getData('text');
            const numbersOnly = pastedData.replace(/\D/g, '').substring(0, 4);

            console.log('ペースト:', pastedData, '数字のみ:', numbersOnly);

            if (numbersOnly.length <= 2) {
                e.target.value = numbersOnly;
            } else {
                e.target.value = numbersOnly.substring(0, 2) + '/' + numbersOnly.substring(2);
            }

            setTimeout(() => {
                e.target.setSelectionRange(e.target.value.length, e.target.value.length);
            }, 0);
        });

        console.log('有効期限フィールドの初期化完了');
    }

    // セキュリティコードの入力制限
    const securityCodeInput = document.getElementById('security-code');
    if (securityCodeInput) {
        securityCodeInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 3) {
                value = value.substring(0, 3);
            }
            e.target.value = value;
        });
    }

    // 電話番号のフォーマット処理
    const phoneNumberInput = document.getElementById('phone-number');
    if (phoneNumberInput) {
        phoneNumberInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/[^0-9-]/g, '');
            e.target.value = value;
        });
    }

    // カード名義の大文字変換処理
    const cardNameInput = document.getElementById('card-name');
    if (cardNameInput) {
        cardNameInput.addEventListener('input', function(e) {
            let value = e.target.value;
            // 英字を大文字に変換、スペースは保持
            value = value.replace(/[a-z]/g, function(match) {
                return match.toUpperCase();
            });
            e.target.value = value;
        });
    }

    // フォーム送信処理
    paymentForm.addEventListener('submit', function(e) {
        e.preventDefault();

        // 送信ボタンを無効化
        setButtonLoading(true);

        // バリデーション実行
        if (!validateForm()) {
            setButtonLoading(false);
            return;
        }

        // 支払い処理を実行
        processPayment();
    });

    // バリデーション関数
    function validateForm() {
        const selectedMethod = document.querySelector('input[name="payment-method"]:checked').value;
        let isValid = true;

        clearAllErrors();

        if (selectedMethod === 'credit-card') {
            isValid = validateCreditCardForm();
        } else if (selectedMethod === 'convenience') {
            isValid = validateConvenienceForm();
        } else if (selectedMethod === 'paypay') {
            // PayPayは特別なバリデーションは不要
            isValid = true;
        }

        return isValid;
    }

    function validateCreditCardForm() {
        let isValid = true;

        const cardNumber = document.getElementById('card-number').value.replace(/\s/g, '');
        const expiryDate = document.getElementById('expiry-date').value;
        const securityCode = document.getElementById('security-code').value;
        const cardName = document.getElementById('card-name').value.trim();

        if (!validateCardNumber(cardNumber)) {
            isValid = false;
        }

        if (!validateExpiryDate(expiryDate)) {
            isValid = false;
        }

        if (!validateSecurityCode(securityCode)) {
            isValid = false;
        }

        if (!validateCardName(cardName)) {
            isValid = false;
        }

        return isValid;
    }

    function validateConvenienceForm() {
        const phoneNumber = document.getElementById('phone-number').value.trim();

        // 電話番号は任意なので、入力されている場合のみバリデーション
        if (phoneNumber && phoneNumber.length > 0 && !validatePhoneNumber(phoneNumber)) {
            return false;
        }

        return true;
    }

    function validateCardNumber(cardNumber) {
        if (cardNumber.length !== 16) {
            showError('card-number-error', 'カード番号は16桁で入力してください');
            return false;
        }

        if (!/^\d{16}$/.test(cardNumber)) {
            showError('card-number-error', 'カード番号は数字のみで入力してください');
            return false;
        }

        clearError('card-number-error');
        return true;
    }

    function validateExpiryDate(expiryDate) {
        if (!/^\d{2}\/\d{2}$/.test(expiryDate)) {
            showError('expiry-date-error', 'MM/YY形式で入力してください');
            return false;
        }

        const [month, year] = expiryDate.split('/').map(num => parseInt(num, 10));

        if (month < 1 || month > 12) {
            showError('expiry-date-error', '月は01-12で入力してください');
            return false;
        }

        const currentYear = new Date().getFullYear() % 100;
        const currentMonth = new Date().getMonth() + 1;

        if (year < currentYear || (year === currentYear && month < currentMonth)) {
            showError('expiry-date-error', '有効期限が過去の日付です');
            return false;
        }

        clearError('expiry-date-error');
        return true;
    }

    function validateSecurityCode(securityCode) {
        if (securityCode.length !== 3) {
            showError('security-code-error', 'セキュリティコードは3桁で入力してください');
            return false;
        }

        if (!/^\d{3}$/.test(securityCode)) {
            showError('security-code-error', 'セキュリティコードは数字のみで入力してください');
            return false;
        }

        clearError('security-code-error');
        return true;
    }

    function validateCardName(cardName) {
        if (cardName.length === 0) {
            showError('card-name-error', 'カード名義を入力してください');
            return false;
        }

        if (!/^[A-Za-z\s]+$/.test(cardName)) {
            showError('card-name-error', 'カード名義は英字で入力してください');
            return false;
        }

        clearError('card-name-error');
        return true;
    }

    function validatePhoneNumber(phoneNumber) {
        const phoneClean = phoneNumber.replace(/[-\s()]/g, '');

        if (!/^0\d{9,10}$/.test(phoneClean)) {
            showError('phone-number-error', '正しい電話番号を入力してください（例：090-1234-5678）');
            return false;
        }

        clearError('phone-number-error');
        return true;
    }

    // 支払い処理（改善版のエラーハンドリング）
    function processPayment() {
        const selectedMethod = document.querySelector('input[name="payment-method"]:checked').value;
        const amount = parseInt(document.getElementById('payment-amount').textContent.replace(',', ''));

        let paymentData = {
            payment_method: selectedMethod,
            amount: amount
        };

        // 支払い方法別のデータ収集
        if (selectedMethod === 'credit-card') {
            paymentData.card_number = document.getElementById('card-number').value;
            paymentData.expiry_date = document.getElementById('expiry-date').value;
            paymentData.security_code = document.getElementById('security-code').value;
            paymentData.card_name = document.getElementById('card-name').value;
        } else if (selectedMethod === 'convenience') {
            paymentData.phone_number = document.getElementById('phone-number').value;
        }

        // ローディング表示
        showLoadingOverlay();

        // APIリクエスト送信
        fetch('/process_payment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(paymentData)
        })
        .then(async response => {
            const data = await response.json();

            hideLoadingOverlay();
            setButtonLoading(false);

            // レスポンスのステータスコードをチェック
            if (!response.ok) {
                console.error('HTTP Error:', response.status, response.statusText);
                console.error('Response data:', data);

                if (response.status === 401) {
                    // 認証エラーの場合
                    showGeneralError('ログインが必要です。ログインページに移動してください。');
                    // 必要に応じてログインページへリダイレクト
                    // setTimeout(() => { window.location.href = '/login'; }, 2000);
                    return;
                } else if (response.status >= 500) {
                    // サーバーエラーの場合
                    showGeneralError('サーバーでエラーが発生しました。管理者に連絡してください。');
                    return;
                }
            }

            if (data.success) {
                // 支払い成功時の処理
                handlePaymentSuccess(data);
            } else {
                // 支払い失敗時の処理
                handlePaymentError(data);
            }
        })
        .catch(error => {
            hideLoadingOverlay();
            setButtonLoading(false);
            console.error('Network Error:', error);
            showGeneralError('通信エラーが発生しました。インターネット接続を確認してからもう一度お試しください。');
        });
    }

    function handlePaymentSuccess(data) {
        // セッションストレージに結果を保存
        sessionStorage.setItem('paymentResult', JSON.stringify(data));

        // 支払い完了ページへリダイレクト
        window.location.href = '/pay_comp';
    }

    function handlePaymentError(data) {
        if (data.errors && Array.isArray(data.errors)) {
            // 個別のエラーを表示
            data.errors.forEach(error => {
                showGeneralError(error);
            });
        } else if (data.message) {
            showGeneralError(data.message);
        } else {
            showGeneralError('支払い処理でエラーが発生しました。');
        }
    }

    // UI制御関数
    function setButtonLoading(isLoading) {
        const btnText = submitButton.querySelector('.btn-text');
        const spinner = submitButton.querySelector('.loading-spinner');

        if (isLoading) {
            submitButton.disabled = true;
            btnText.style.display = 'none';
            spinner.style.display = 'inline';
            submitButton.classList.add('loading');
        } else {
            submitButton.disabled = false;
            btnText.style.display = 'inline';
            spinner.style.display = 'none';
            submitButton.classList.remove('loading');
        }
    }

    function showLoadingOverlay() {
        loadingOverlay.style.display = 'flex';
    }

    function hideLoadingOverlay() {
        loadingOverlay.style.display = 'none';
    }

    function showError(elementId, message) {
        const errorElement = document.getElementById(elementId);
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.style.display = 'block';
        }
    }

    function clearError(elementId) {
        const errorElement = document.getElementById(elementId);
        if (errorElement) {
            errorElement.textContent = '';
            errorElement.style.display = 'none';
        }
    }

    function clearAllErrors() {
        const errorElements = document.querySelectorAll('.error-message');
        errorElements.forEach(element => {
            element.textContent = '';
            element.style.display = 'none';
        });

        generalErrorsDiv.innerHTML = '';
        generalErrorsDiv.style.display = 'none';
    }

    function showGeneralError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-item';
        errorDiv.textContent = message;

        generalErrorsDiv.appendChild(errorDiv);
        generalErrorsDiv.style.display = 'block';
    }
});