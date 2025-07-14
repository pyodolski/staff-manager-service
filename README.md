Staff Manager Project

고기당 직원 출퇴근 관리 웹 애플리케이션

배포 URL: https://staff-manager-project.onrender.com
배포 환경: Render + Railway (2025.07.12 ~ 운영 중)
Repository: 공개(Public) | auth.py는 보안을 위해 Pravite에서 관리

[주요 기능]
Google 계정 로그인 (OAuth2.0 기반)
FullCalendar 기반 월별 출근 캘린더
출퇴근 시간 등록 및 자동 근무 시간 계산
월별 총 근무 시간, 시급, 총 급여, 소득세/지방세 및 실지급액 자동 계산
모바일 대응 UI
[기술 스택]

Frontend: HTML, CSS, JavaScript, FullCalendar
Backend: Python (Flask), Jinja
Database: MySQL (Railway)
배포: Render (Flask 서버) + Railway (DB Hosting)

[보안 참고 사항]
auth.py는 Google OAuth2 Client ID/Secret을 포함하므로 .gitignore 처리되어 별도 관리됩니다.
기타 민감 정보는 .env 또는 배포 플랫폼의 환경변수로 설정됩니다.
