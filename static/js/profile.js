let isEditMode = false;

let origName,origemail,origphone,origbirth;

origNick = document.getElementById('edit-nick').value;
origName = document.getElementById('edit-name').value;
origemail = document.getElementById('edit-email').value;
origphone = document.getElementById('edit-phone').value;
origbirth = document.getElementById('edit-birth').value;




function toggleEditMode() {
    isEditMode = !isEditMode;
    const displays = document.querySelectorAll('.info-display span');
    const inputs = document.querySelectorAll('.info-display input');
    const editActions = document.querySelector('.edit-actions');

    if (isEditMode) {
        // 編集モードに切り替え
        displays.forEach(span => span.style.display = 'none');
        inputs.forEach(input => input.style.display = 'block');
        editActions.style.display = 'flex';
    
    } else {
        // 表示モードに切り替え
        displays.forEach(span => span.style.display = 'inline');
        inputs.forEach(input => input.style.display = 'none');
        editActions.style.display = 'none';
    }
}

function saveProfile() {
    // 入力値を取得
    const nick = document.getElementById('edit-nick').value;
    const name = document.getElementById('edit-name').value;
    const email = document.getElementById('edit-email').value;
    const phone = document.getElementById('edit-phone').value;
    const birth = document.getElementById('edit-birth').value;

    // ★変更: accountId はJavaScriptから送る必要がなくなりました。
    // Flask側でセッションから取得するため、この部分のコードは不要です。

    // データをFlaskエンドポイントにPOST
    fetch('/add_account', { // Flaskのルート名はそのまま
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            accountName: nick,
            realName: name,       // JSのnameをrealNameとして送信
            emailAddress: email,
            phoneNumber: phone,
            birthDate: birth,
        })
    })
    .then(response => {
        // HTTPステータスコードをチェックし、エラーの場合はJSON解析前に処理
        if (!response.ok) {
            // エラーレスポンスのJSONを解析して、具体的なエラーメッセージを表示
            return response.json().then(errorData => {
                throw new Error(errorData.message || `HTTPエラー: ${response.status}`);
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // 成功時の処理 (前回のJSと同じ)
            // 表示を更新
            document.getElementById('display-nick').textContent = nick;
            document.getElementById('display-name').textContent = name;
            document.getElementById('display-email').textContent = email;
            document.getElementById('display-phone').textContent = phone;

            // 生年月日をフォーマット
            const birthDate = new Date(birth);
            // new Date() が不正な日付文字列を受け取ると Invalid Date になる可能性があるのでチェック
            const formattedBirth = (isNaN(birthDate.getTime())) ? '' : `${birthDate.getFullYear()}年${birthDate.getMonth() + 1}月${birthDate.getDate()}日`;
            document.getElementById('display-birth').textContent = formattedBirth;

            // プロフィール名も更新
            document.getElementById('profile-name').textContent = nick;

            // 編集モードを終了
            toggleEditMode();

            // 保存完了メッセージ
            showNotification('プロフィールを更新しました', 'success');

        } else {
            alert('エラーが発生しました: ' + data.message);
        }
    })
    .catch(error => {
        console.error('通信またはサーバーエラー:', error);
        alert('プロフィールの更新中にエラーが発生しました: ' + error.message);
    });
}




function cancelEdit() {
    // 元のデータに戻す
    document.getElementById('edit-name').value = origName;
    document.getElementById('edit-email').value = origemail;
    document.getElementById('edit-phone').value = origphone;
    document.getElementById('edit-birth').value = origbirth;
    
    // 編集モードを終了
    toggleEditMode();
}

function editAvatar() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.onchange = function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                document.getElementById('avatar-img').src = e.target.result;
                showNotification('プロフィール画像を更新しました', 'success');
            };
            reader.readAsDataURL(file);
        }
    };
    input.click();
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#27ae60' : '#3498db'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// CSS アニメーション
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);


document.addEventListener('DOMContentLoaded', () => {
    
    // id="avatar-plus-button" を持つ要素を取得
    const plusButton = document.getElementById('avatar-plus-button');

    // 要素が取得できた場合のみ、処理を続ける
    if (plusButton) {
        // plusButtonがクリックされたら、中の処理を実行する
        plusButton.addEventListener('click', () => {
            // 開発者ツールのコンソールにメッセージを出力
            console.log('＋マークがクリックされました！');
        });
    }
});