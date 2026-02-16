function showFlashMessage(message, type = "success") {
  // flash-container が存在しない場合は作成
  let flashContainer = document.querySelector(".flash-container");
  if (!flashContainer) {
    flashContainer = document.createElement("div");
    flashContainer.className = "flash-container";
    document.body.appendChild(flashContainer);
  }

  // フラッシュメッセージ要素を作成
  const flash = document.createElement("div");
  flash.className = `flash-message ${type}`;
  flash.textContent = message;

  // 表示
  flashContainer.appendChild(flash);

  // 1秒後にフェードアウト、さらに1秒後に削除
  setTimeout(() => {
    flash.style.transition = "opacity 1s ease";
    flash.style.opacity = 0;
    setTimeout(() => flash.remove(), 1000);
  }, 1000);
}

window.addEventListener('DOMContentLoaded', () => {
  const flashes = document.querySelectorAll('.flash-message');
  flashes.forEach(flash => {
    setTimeout(() => {
      flash.style.transition = "opacity 1s ease";
      flash.style.opacity = 0;
      setTimeout(() => flash.remove(), 1000);
    }, 2000);
  });
});
