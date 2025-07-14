# Staff Manager Project

직원 출퇴근 및 근무 내역을 효율적으로 관리할 수 있는 웹 애플리케이션입니다. Google OAuth2를 통한 로그인 기능과 캘린더 기반의 출퇴근 기록 관리, 급여 자동 계산 기능을 제공합니다.

## 서비스 정보

- **서비스 주소**: https://staff-manager-project.onrender.com
- **배포 환경**: Render (서버) + Railway (MySQL DB)
- **서비스 시작일**: 2025년 7월 12일
- **공개 저장소**: `auth.py` 등 민감 정보는 제외하고 공개

## 주요 기능

- Google 계정을 통한 사용자 로그인 (OAuth 2.0)
- FullCalendar 기반의 출퇴근 캘린더 UI
- 출근/퇴근 시간 등록 및 총 근무 시간 자동 계산
- 시급 기반의 월별 총 급여 및 실지급액 계산
- 소득세(3%) 및 지방세(0.3%) 자동 공제
- 월별 필터 및 조회 기능
- 반응형 UI (모바일 최적화)

## 기술 스택

- **Frontend**: HTML5, CSS3, JavaScript, FullCalendar
- **Backend**: Python (Flask), Jinja2
- **Database**: MySQL (Hosted on Railway)
- **Deployment**: Render (Flask App), Railway (DB Hosting)

## 보안 및 구성

- `auth.py`는 Google OAuth Client 정보 보호를 위해 저장소에서 제외되어 있으며, 환경변수로 분리하여 관리합니다.
- 민감한 정보는 `.env` 혹은 Render/Railway의 환경변수 설정을 통해 주입됩니다.

## 향후 개선 예정 사항

- 관리자 권한에 따른 사용자 승인 및 미승인 사유 전달 기능
- 출근 기록 수정 및 삭제 기능
- 급여 내역 다운로드 (PDF/Excel) 기능

