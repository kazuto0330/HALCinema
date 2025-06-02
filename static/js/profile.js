let isEditMode = false;
let originalData = {};

function toggleEditMode() {
    isEditMode = !isEditMode;
    const displays = document.querySelectorAll('.info-display span');
    const inputs = document.querySelectorAll('.info-display input');
    const editActions = document.querySelector('.edit-actions');
    const editBtn = document.querySelector('.edit-profile-btn');

    if (isEditMode) {
        // 編集モードに切り替え
        displays.forEach(span => span.style.display = 'none');
        inputs.forEach(input => input.style.display = 'block');
        editActions.style.display = 'flex';
        editBtn.textContent = '編集をキャンセル';
        editBtn.style.background = '#e74c3c';
        
        // 元のデータを保存
        originalData = {
            name: document.getElementById('edit-name').value,
            email: document.getElementById('edit-email').value,
            phone: document.getElementById('edit-phone').value,
            birth: document.getElementById('edit-birth').value
        };
    } else {
        // 表示モードに切り替え
        displays.forEach(span => span.style.display = 'inline');
        inputs.forEach(input => input.style.display = 'none');
        editActions.style.display = 'none';
        editBtn.textContent = 'プロフィール編集';
        editBtn.style.background = '#3498db';
    }
}

function saveProfile() {
    // 入力値を取得
    const name = document.getElementById('edit-name').value;
    const email = document.getElementById('edit-email').value;
    const phone = document.getElementById('edit-phone').value;
    const birth = document.getElementById('edit-birth').value;

    // 表示を更新
    document.getElementById('display-name').textContent = name;
    document.getElementById('display-email').textContent = email;
    document.getElementById('display-phone').textContent = phone;
    
    // 生年月日をフォーマット
    const birthDate = new Date(birth);
    const formattedBirth = `${birthDate.getFullYear()}年${birthDate.getMonth() + 1}月${birthDate.getDate()}日`;
    document.getElementById('display-birth').textContent = formattedBirth;
    
    // プロフィール名も更新
    document.getElementById('profile-name').textContent = name;

    // 編集モードを終了
    toggleEditMode();
    
    // 保存完了メッセージ
    showNotification('プロフィールを更新しました', 'success');
}

function cancelEdit() {
    // 元のデータに戻す
    document.getElementById('edit-name').value = originalData.name;
    document.getElementById('edit-email').value = originalData.email;
    document.getElementById('edit-phone').value = originalData.phone;
    document.getElementById('edit-birth').value = originalData.birth;
    
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

// ジャンルタグのクリックイベント
document.querySelectorAll('.genre-tag').forEach(tag => {
    tag.addEventListener('click', function() {
        this.classList.toggle('active');
    });
});

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