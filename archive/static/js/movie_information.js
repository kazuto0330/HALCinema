document.addEventListener('DOMContentLoaded', function () {
  // 対象の曜日一覧
    const weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

  // 各 dayCard にクリックイベントを設定
    document.querySelectorAll('.dayCard').forEach(card => {
    card.addEventListener('click', () => {
      // 一度すべてのスケジュールを非表示にする
        document.querySelectorAll('.reservationSchedule').forEach(schedule => {
        schedule.classList.add('hidden');
        });

      // 曜日クラス（例: "Tue"）を取得
        const selectedDay = [...card.classList].find(cls => weekdays.includes(cls));

        if (selectedDay) {
        // 対応するスケジュールIDを探して表示
        const targetSchedule = document.getElementById(`schedule-${selectedDay}`);
        if (targetSchedule) {
            targetSchedule.classList.remove('hidden');
        }
        }
    });
    });
});
