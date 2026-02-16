import base64
import io
from datetime import timedelta
import qrcode
from flask import render_template
from playwright.sync_api import sync_playwright

class TicketGenerator:
    """
    Playwrightを使用してチケットPDFを生成するクラス。
    """
    def __init__(self):
        pass

    def _generate_qr_base64(self, data):
        """
        QRコードを生成し、Base64エンコードされた文字列として返す。
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    def _process_ticket_data(self, db_data_list):
        """
        DBからのデータをテンプレート用のフォーマットに変換する。
        """
        if not db_data_list:
            return []
            
        # 単価計算（簡易的に総額÷枚数）
        total_amount = db_data_list[0].get('totalReservationAmount', 0)
        count = len(db_data_list)
        unit_price = int(total_amount / count) if count > 0 else 0
        
        processed_tickets = []
        for data in db_data_list:
            # 日付フォーマット
            screening_date = data['scheduledScreeningDate']
            weekday_jp = ['月','火','水','木','金','土','日'][screening_date.weekday()]
            date_str = screening_date.strftime(f"%Y/%m/%d({weekday_jp})")
            
            # 時間フォーマット
            start_time = data['screeningStartTime']
            if isinstance(start_time, timedelta):
                seconds = int(start_time.total_seconds())
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                time_str = f"{hours:02}:{minutes:02}"
            else:
                time_str = start_time.strftime("%H:%M")

            # QRコード用データ
            seat_res_id = data['seatReservationId']
            qr_content = f"HALCINEMA:{seat_res_id}"
            qr_data = self._generate_qr_base64(qr_content)

            ticket_info = {
                'movie_title': data['movieTitle'],
                'date_str': date_str,
                'time_str': time_str,
                'theater_number': data['theaterNumber'],
                'seat_number': data['seatNumber'],
                'price': "{:,}".format(unit_price),
                'seat_reservation_id': seat_res_id,
                'qr_data': qr_data
            }
            processed_tickets.append(ticket_info)
            
        return processed_tickets

    def generate_tickets_pdf(self, db_data_list, layout_mode='a4'):
        """
        DBから取得したチケットデータのリストを受け取り、それらを連結したPDFバイナリデータを返す。
        
        Args:
            db_data_list (list): DBから取得した辞書のリスト。
            layout_mode (str): 'a4' (デフォルト) または 'single'
        
        Returns:
            bytes: PDFファイルのバイナリデータ
        """
        
        # データをテンプレート用に加工
        processed_tickets = self._process_ticket_data(db_data_list)
        
        # テンプレートレンダリング
        try:
            full_html_content = render_template(
                'ticket_card.html', 
                tickets=processed_tickets,
                layout_mode=layout_mode
            )
        except Exception as e:
            print(f"Template rendering error: {e}")
            raise e
        
        pdf_bytes = None
        
        try:
            with sync_playwright() as p:
                # ブラウザ起動 (ヘッドレスモード)
                browser = p.chromium.launch(
                    args=['--disable-dev-shm-usage', '--no-sandbox']
                )
                page = browser.new_page()
                
                # HTMLコンテンツを設定
                page.set_content(full_html_content)
                
                # PDF生成
                # layout_mode='single' の場合は CSS @page でサイズ指定されているので、
                # prefer_css_page_size=True にすれば自動的にそのサイズになる。
                # 'a4' の場合も CSS @page size: A4 となっているので同様。
                
                pdf_bytes = page.pdf(
                    print_background=True,
                    prefer_css_page_size=True
                )
                
                browser.close()
                
        except Exception as e:
            print(f"Playwright PDF generation error: {e}")
            raise e
            
        return pdf_bytes

    def generate_receipt_pdf(self, receipt_data):
        """
        領収書PDFを生成する。
        
        Args:
            receipt_data (dict): テンプレートに渡すデータの辞書。
        
        Returns:
            bytes: PDFファイルのバイナリデータ
        """
        try:
            full_html_content = render_template(
                'receipt.html', 
                **receipt_data
            )
        except Exception as e:
            print(f"Receipt Template rendering error: {e}")
            raise e
        
        pdf_bytes = None
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    args=['--disable-dev-shm-usage', '--no-sandbox']
                )
                page = browser.new_page()
                page.set_content(full_html_content)
                
                pdf_bytes = page.pdf(
                    format='A4',
                    print_background=True,
                    margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'}
                )
                
                browser.close()
                
        except Exception as e:
            print(f"Playwright PDF generation error (Receipt): {e}")
            raise e
            
        return pdf_bytes
