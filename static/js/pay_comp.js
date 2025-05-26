/* script.js */
document.addEventListener('DOMContentLoaded', function() {
    const completeButton = document.getElementById('completeButton');

    completeButton.addEventListener('click', handleComplete);
});

function handleComplete() {
    // ここに完了ボタンがクリックされた時の処理を追加
    alert('処理が完了しました。');
    // 実際の実装では、前のページに戻る、ホームページに移動するなどの処理を行います
    // window.history.back(); // 前のページに戻る
    // window.location.href = '/'; // ホームページに移動
}