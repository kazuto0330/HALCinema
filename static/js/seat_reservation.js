document.addEventListener('DOMContentLoaded', () => {

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
    });
  });

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
      const rowDiv = seat.closest('.row');
      const rowLabelElem = rowDiv.querySelector('.label');
      const rowLabel = rowLabelElem ? rowLabelElem.textContent.trim() : '';
      const seatIndex = Array.from(rowDiv.querySelectorAll('.seat')).indexOf(seat) + 1;

      selectedSeats.push({
        row: rowLabel,
        seatNumber: seatIndex
      });
    });

    if (selectedSeats.length === 0) {
      alert('座席を選択してください');
      return;
    }

    console.log("送信する座席情報:", selectedSeats);

    fetch(`/seat_reservation/${showingId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ seats: selectedSeats })
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
});
