// 座席ボタンをクリックで色を切り替える
document.querySelectorAll('.seat').forEach(button => {
  button.addEventListener('click', () => {
    button.classList.toggle('taken');
  });
});