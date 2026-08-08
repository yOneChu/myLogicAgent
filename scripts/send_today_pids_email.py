#!/usr/bin/env python3
"""
금일 수정된 PID 목록을 조회하여 Outlook을 통해 예쁜 HTML 테이블 형식의 메일로 발송하는 스크립트입니다.
"""

import csv
import sys
from pathlib import Path
from typing import Dict, List, Any

try:
    import win32com.client as win32
except ImportError:
    win32 = None

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = Path(__file__).resolve().parent.parent
RECENT_CSV = ROOT_DIR / "output_csv" / "recent_pids.csv"


def filter_today_pids(csv_path: Path, target_date: str = "2026-08-07") -> List[Dict[str, str]]:
    """
    최근 PID 목록 CSV 파일에서 금일(target_date) 등록/수정된 PID 항목을 필터링하는 함수입니다.
    
    :param csv_path: 최근 PID CSV 경로
    :param target_date: 필터링 대상 날짜 (YYYY-MM-DD)
    :return: 금일 수정된 PID 리스트
    """
    today_pids = []
    if not csv_path.exists():
        print(f"오류: {csv_path} 파일이 존재하지 않습니다.")
        return today_pids
        
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            reg_date = row.get('REG_DATE', '').strip()
            if reg_date.startswith(target_date):
                today_pids.append(row)
                
    return today_pids


def generate_html_email_body(today_pids: List[Dict[str, str]], target_date: str = "2026-08-07") -> str:
    """
    금일 수정된 PID 리스트를 받아 가독성이 높고 아름다운 HTML 스타일의 이메일 본문을 생성하는 함수입니다.
    
    :param today_pids: 금일 PID 데이터 리스트
    :param target_date: 기준 일자
    :return: HTML 본문 문자열
    """
    total_cnt = len(today_pids)
    
    table_rows_html = ""
    for idx, item in enumerate(today_pids, start=1):
        bg_color = "#F8F9FA" if idx % 2 == 0 else "#FFFFFF"
        pid = item.get("PID", "-")
        version = item.get("VERSION", "-")
        houid = item.get("HOUID", "-")
        reg_date = item.get("REG_DATE", "-").replace("T", " ").replace(".000+00:00", "")
        
        table_rows_html += f"""
        <tr style="background-color: {bg_color}; text-align: center;">
            <td style="padding: 10px 12px; border-bottom: 1px solid #E9ECEF; font-size: 14px;">{idx}</td>
            <td style="padding: 10px 12px; border-bottom: 1px solid #E9ECEF; font-size: 14px; font-weight: bold; color: #004085;">{pid}</td>
            <td style="padding: 10px 12px; border-bottom: 1px solid #E9ECEF; font-size: 14px; color: #212529;">v{version}</td>
            <td style="padding: 10px 12px; border-bottom: 1px solid #E9ECEF; font-size: 14px; color: #495057;">{houid}</td>
            <td style="padding: 10px 12px; border-bottom: 1px solid #E9ECEF; font-size: 14px; color: #6C757D;">{reg_date}</td>
        </tr>
        """

    if not today_pids:
        table_rows_html = """
        <tr>
            <td colspan="5" style="padding: 20px; text-align: center; color: #6C757D; font-size: 14px;">금일 수정/등록된 PID 항목이 없습니다.</td>
        </tr>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
    </head>
    <body style="font-family: 'Malgun Gothic', '맑은 고딕', sans-serif; background-color: #F4F6F9; margin: 0; padding: 20px;">
        <div style="max-width: 750px; margin: 0 auto; background-color: #FFFFFF; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); overflow: hidden; border: 1px solid #DEE2E6;">
            
            <!-- Header section -->
            <div style="background: linear-gradient(135deg, #0056B3 0%, #003366 100%); color: #FFFFFF; padding: 25px 30px;">
                <h2 style="margin: 0; font-size: 22px; font-weight: 600;">📋 금일 수정/등록 PID 현황 보고</h2>
                <p style="margin: 8px 0 0 0; font-size: 14px; opacity: 0.9;">기준 일자: {target_date} | 총 건수: <strong>{total_cnt}건</strong></p>
            </div>
            
            <!-- Body content section -->
            <div style="padding: 25px 30px;">
                <p style="font-size: 15px; color: #333333; line-height: 1.6; margin-top: 0;">
                    안녕하세요,<br>
                    <strong>{target_date}</strong> 자 기준 데이터베이스에 신규 등록 및 수정 반영된 PID 목록입니다.
                </p>
                
                <!-- Table section -->
                <table style="width: 100%; border-collapse: collapse; margin-top: 20px; border-top: 2px solid #0056B3;">
                    <thead>
                        <tr style="background-color: #E9ECEF; color: #333333;">
                            <th style="padding: 12px 10px; font-size: 14px; font-weight: 600; text-align: center; border-bottom: 2px solid #DEE2E6;">No</th>
                            <th style="padding: 12px 10px; font-size: 14px; font-weight: 600; text-align: center; border-bottom: 2px solid #DEE2E6;">PID명</th>
                            <th style="padding: 12px 10px; font-size: 14px; font-weight: 600; text-align: center; border-bottom: 2px solid #DEE2E6;">버전 (Version)</th>
                            <th style="padding: 12px 10px; font-size: 14px; font-weight: 600; text-align: center; border-bottom: 2px solid #DEE2E6;">헤더 ID (HOUID)</th>
                            <th style="padding: 12px 10px; font-size: 14px; font-weight: 600; text-align: center; border-bottom: 2px solid #DEE2E6;">등록/수정 일시</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows_html}
                    </tbody>
                </table>
                
                <!-- Notice section -->
                <div style="margin-top: 25px; padding: 15px; background-color: #E8F4FD; border-left: 4px solid #0056B3; border-radius: 4px; font-size: 13px; color: #004085;">
                    💡 <strong>안내 사항:</strong> 세부 라인(`ADDR/GOTO`, `SPEC/CON`, `KEY/VAL`) 변경사항 분석이 필요하신 경우 언제든지 말씀해 주세요.
                </div>
            </div>
            
            <!-- Footer section -->
            <div style="background-color: #F8F9FA; padding: 15px 30px; text-align: center; border-top: 1px solid #E9ECEF; font-size: 12px; color: #868E96;">
                본 메일은 PLM 로직 에이전트 시스템에서 자동으로 생성 및 발송되었습니다.
            </div>
        </div>
    </body>
    </html>
    """
    return html_content


def send_email_via_outlook(to_email: str, subject: str, html_body: str) -> bool:
    """
    Outlook 클라이언트를 사용하여 HTML 형식 메일을 발송하는 함수입니다.
    
    :param to_email: 수신자 메일 주소
    :param subject: 메일 제목
    :param html_body: HTML 메일 본문
    :return: 발송 성공 여부
    """
    if win32 is None:
        print("오류: pywin32 패키지가 설치되어 있지 않습니다.")
        return False
        
    try:
        outlook = win32.Dispatch('Outlook.Application')
        mail = outlook.CreateItem(0) # 0: olMailItem
        mail.To = to_email
        mail.Subject = subject
        mail.HTMLBody = html_body
        mail.Send()
        print(f"[성공] HTML 이메일을 성공적으로 발송했습니다. (수신자: {to_email})")
        return True
    except Exception as exc:
        print(f"[오류] 이메일 발송 중 예외 발생: {exc}")
        return False


def main():
    """
    메인 실행 함수입니다. CSV에서 금일 PID 데이터를 필터링하고 Outlook 이메일을 발송합니다.
    """
    target_date = "2026-08-07"
    to_email = "younghwan.kim@hyundaielevator.com"
    subject = f"[보고] 금일({target_date}) 수정 및 등록 PID 현황 목록"
    
    print(f"[1/3] 최근 PID 목록에서 {target_date}자 데이터를 추출합니다...")
    today_pids = filter_today_pids(RECENT_CSV, target_date)
    print(f" -> 금일 수정된 PID 건수: {len(today_pids)}건")
    
    print(f"[2/3] HTML 이메일 본문을 생성합니다...")
    html_body = generate_html_email_body(today_pids, target_date)
    
    print(f"[3/3] Outlook을 통해 이메일을 발송합니다... (수신자: {to_email})")
    success = send_email_via_outlook(to_email, subject, html_body)
    
    if success:
        print("\n🎉 이메일 발송이 성공적으로 완료되었습니다!")
    else:
        print("\n⚠️ 이메일 발송 실패")


if __name__ == "__main__":
    main()
