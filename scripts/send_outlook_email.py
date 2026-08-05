import win32com.client as win32

def send_email_via_outlook(to_email: str, subject: str, body: str) -> bool:
    """
    Microsoft Outlook 클라이언트를 사용하여 메일을 발송하는 주요 함수입니다.

    :param to_email: 수신자 이메일 주소
    :param subject: 메일 제목
    :param body: 메일 본문 내용
    :return: 발송 성공 여부 (Boolean)
    """
    try:
        # Microsoft Outlook 애플리케이션 COM 객체에 연결 (실행 중이 아니면 자동 실행됨)
        outlook = win32.Dispatch('Outlook.Application')
        
        # 메일 객체 생성 (0은 olMailItem을 의미함)
        mail = outlook.CreateItem(0)
        
        # 수신자, 제목, 본문 설정
        mail.To = to_email
        mail.Subject = subject
        mail.Body = body
        
        # 메일 보내기 실행
        mail.Send()
        print(f"[성공] 메일을 성공적으로 발송했습니다. (수신자: {to_email})")
        return True
    except Exception as e:
        print(f"[오류] 메일 발송 실패: {e}")
        return False

if __name__ == "__main__":
    # 발송 대상 이메일 주소
    target_email = "younghwan.kim@hyundaielevator.com"
    # 메일 제목
    mail_subject = "안녕하세요"
    # 메일 본문 내용
    mail_body = "안녕하세요!\n\n요청하신 메일입니다."
    
    # 메일 발송 함수 수행
    send_email_via_outlook(to_email=target_email, subject=mail_subject, body=mail_body)
