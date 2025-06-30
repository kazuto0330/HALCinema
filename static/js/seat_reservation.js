document.addEventListener('DOMContentLoaded', () => {
  // 1席あたりの料金（円）
  const PRICE_PER_SEAT = 1800;

  // 予約済み座席のlockクラス付与
  document.querySelectorAll('.hall .row').forEach(row => {
    const rowLabelElem = row.querySelector('.label');
    if (!rowLabelElem) return;
    const rowLabel = rowLabelElem.textContent.trim();

    const seats = row.querySelectorAll('.seat');
    seats.forEach((seat, idx) => {
      const seatNumber = idx + 1;
      const seatId = `${rowLabel}-${seatNumber}`;
      if (reservedSeats.includes(seatId)) {
        seat.classList.add('lock');
      }
    });
  });

  // 料金表示エリアを作成
  createPriceDisplay();

  // リップルエフェクト
  document.querySelectorAll('button').forEach(button => {
    button.addEventListener('click', function (e) {
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

  // 座席クリック（イベント委譲）
  document.querySelectorAll('.hall').forEach(hall => {
    hall.addEventListener('click', e => {
      const seat = e.target.closest('.seat');
      if (!seat) return;
      if (seat.classList.contains('lock')) return; // 予約済みは選択不可

      seat.classList.toggle('taken');

      // デバッグ: 選択された座席の情報を表示
      if (seat.classList.contains('taken')) {
        const seatInfo = getSeatInfo(seat);
        console.log('座席選択:', seatInfo);
      }

      // 料金を更新
      updatePriceDisplay();
    });
  });

  // 座席情報を取得する関数
  function getSeatInfo(seatElement) {
    const rowDiv = seatElement.closest('.row');
    const rowLabelElem = rowDiv.querySelector('.label');
    const rowLabel = rowLabelElem ? rowLabelElem.textContent.trim() : '';

    // その行のすべての要素を取得
    const allChildren = Array.from(rowDiv.children);
    const seatIndex = allChildren.indexOf(seatElement);

    // その座席より前にある座席の数を数える
    let seatNumber = 0;
    for (let i = 0; i < seatIndex; i++) {
      if (allChildren[i].classList.contains('seat')) {
        seatNumber++;
      }
    }
    seatNumber++; // 1から始まるようにする

    return {
      row: rowLabel,
      seatNumber: seatNumber
    };
  }

  // Flaskから渡されたshowingId
  const showingId = document.body.dataset.showingId;
  console.log("showingId:", showingId);

  // 予約送信処理
  document.getElementById('submitReservation').addEventListener('click', () => {
    const activeHall = document.querySelector('.hall.active');
    if (!activeHall) {
      alert('シアターを選択してください');
      return;
    }

    const selectedSeats = [];
    activeHall.querySelectorAll('.seat.taken').forEach(seat => {
      const seatInfo = getSeatInfo(seat);
      selectedSeats.push(seatInfo);
    });

    if (selectedSeats.length === 0) {
      alert('座席を選択してください');
      return;
    }

    // 総料金を計算
    const totalAmount = selectedSeats.length * PRICE_PER_SEAT;

    console.log("送信する座席情報:", selectedSeats);
    console.log("総料金:", totalAmount);

    // セッションストレージに料金情報を保存
    sessionStorage.setItem('selectedSeats', JSON.stringify(selectedSeats));
    sessionStorage.setItem('totalAmount', totalAmount.toString());

    fetch(`/seat_reservation/${showingId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        seats: selectedSeats,
        totalAmount: totalAmount
      })
    })
      .then(response => {
        if (!response.ok) throw new Error('予約に失敗しました');
        return response.json();
      })
      .then(data => {
        window.location.href = '/pay';
      })
      .catch(err => {
        alert('通信エラー: ' + err.message);
      });
  });

  // 料金表示エリアを作成する関数
  function createPriceDisplay() {
    const priceContainer = document.createElement('div');
    priceContainer.id = 'price-container';
    priceContainer.innerHTML = `
      <div class="price-display">
        <div class="price-info">
          <span class="seat-count">選択座席数: <span id="seat-count">0</span>席</span>
          <span class="total-price">合計金額: ¥<span id="total-price">0</span></span>
        </div>
        <div class="price-detail">
          <small>1席あたり ¥${PRICE_PER_SEAT.toLocaleString()}</small>
        </div>
      </div>
    `;

    // 予約ボタンの前に挿入
    const submitButton = document.getElementById('submitReservation');
    submitButton.parentNode.insertBefore(priceContainer, submitButton);

    // スタイルを追加
    const priceStyle = document.createElement('style');
    priceStyle.textContent = `
      #price-container {
        margin: 30px auto;
        max-width: 400px;
      }
      
      .price-display {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        text-align: center;
        margin-bottom: 20px;
      }
      
      .price-info {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
        font-size: 16px;
        font-weight: bold;
      }
      
      .price-detail {
        font-size: 12px;
        opacity: 0.8;
      }
      
      #seat-count, #total-price {
        color: #ffeb3b;
        font-weight: bold;
      }
      
      @media (max-width: 480px) {
        .price-info {
          flex-direction: column;
          gap: 8px;
        }
        
        #price-container {
          margin: 20px 10px;
        }
        
        .price-display {
          padding: 15px;
        }
      }
    `;
    document.head.appendChild(priceStyle);
  }

  // 料金表示を更新する関数
  function updatePriceDisplay() {
    const activeHall = document.querySelector('.hall.active');
    if (!activeHall) return;

    const selectedSeats = activeHall.querySelectorAll('.seat.taken');
    const seatCount = selectedSeats.length;
    const totalPrice = seatCount * PRICE_PER_SEAT;

    // 表示を更新
    const seatCountElement = document.getElementById('seat-count');
    const totalPriceElement = document.getElementById('total-price');

    if (seatCountElement && totalPriceElement) {
      seatCountElement.textContent = seatCount;
      totalPriceElement.textContent = totalPrice.toLocaleString();
    }

    // 予約ボタンの状態を更新
    const submitButton = document.getElementById('submitReservation');
    if (seatCount === 0) {
      submitButton.disabled = true;
      submitButton.textContent = '座席を選択してください';
      submitButton.style.opacity = '0.6';
    } else {
      submitButton.disabled = false;
      submitButton.textContent = `${seatCount}席を予約する`;
      submitButton.style.opacity = '1';
    }
  }

  // 初期表示の更新
  updatePriceDisplay();
});