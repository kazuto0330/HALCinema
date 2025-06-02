const selector = document.getElementById('hallSelector');
const halls = document.querySelectorAll('.hall');

selector.addEventListener('change', function () {
  halls.forEach(hall => hall.classList.remove('active'));
  document.getElementById('hall' + this.value).classList.add('active');
});



// ボタンクリック時のフィードバック
document.querySelectorAll('button').forEach(button => {
  button.addEventListener('click', function (e) {
    // リップルエフェクト
    const ripple = document.createElement('span');
    const rect = this.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = e.clientX - rect.left - size / 2;
    const y = e.clientY - rect.top - size / 2;

    ripple.style.cssText = `
                    position: absolute;
                    width: ${size}px;
                    height: ${size}px;
                    left: ${x}px;
                    top: ${y}px;
                    background: radial-gradient(circle, rgba(255,255,255,0.6) 0%, transparent 70%);
                    border-radius: 50%;
                    transform: scale(0);
                    animation: ripple 0.6s linear forwards;
                    pointer-events: none;
                `;

    this.style.position = 'relative';
    this.style.overflow = 'hidden';
    this.appendChild(ripple);

    setTimeout(() => {
      ripple.remove();
    }, 600);
  });
});

// CSSアニメーション追加
const style = document.createElement('style');
style.textContent = `
                @keyframes ripple {
                to {
                transform: scale(2);
                opacity: 0;
            }
            }
                `;
document.head.appendChild(style);


// 座席ボタンをクリックで色を切り替える
document.querySelectorAll('.seat').forEach(button => {
  button.addEventListener('click', () => {
    button.classList.toggle('taken');
  });
});