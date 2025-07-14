from flask import Blueprint, request, jsonify
from datetime import datetime, time, timedelta
from flask_login import current_user, login_required
from models import db, WorkLog

worklog_bp = Blueprint('worklog', __name__, url_prefix='/api/worklog')

# 근무 기록 등록 (덮어쓰기 포함)
@worklog_bp.route('', methods=['POST'])
@login_required
def add_worklog():
    data = request.json

    try:
        work_date = datetime.strptime(data['work_date'], "%Y-%m-%d").date()
        clock_in = time(int(data['clock_in_hour']), int(data['clock_in_minute']))
        clock_out = time(int(data['clock_out_hour']), int(data['clock_out_minute']))

        # 출근-퇴근 시간 계산 (익일 퇴근 가능)
        dt_in = datetime.combine(work_date, clock_in)
        dt_out = datetime.combine(work_date, clock_out)
        if dt_out <= dt_in:
            dt_out += timedelta(days=1)

        total_seconds = (dt_out - dt_in).total_seconds()
        total_hours = total_seconds / 3600.0

        # 이미 등록된 같은 날짜의 기록이 있으면 덮어쓰기
        existing_log = WorkLog.query.filter_by(user_id=current_user.id, work_date=work_date).first()
        if existing_log:
            existing_log.clock_in = clock_in
            existing_log.clock_out = clock_out
            existing_log.total_hours = total_hours
            existing_log.status = 0  # 덮어쓰기 시 다시 대기 상태로
        else:
            new_log = WorkLog(
                user_id=current_user.id,
                work_date=work_date,
                clock_in=clock_in,
                clock_out=clock_out,
                total_hours=total_hours,
                status=0
            )
            db.session.add(new_log)

        db.session.commit()
        return jsonify({"message": "근무 기록 저장 완료"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# 캘린더 표시용 근무 기록 (승인된 것만)
@worklog_bp.route('/events', methods=['GET'])
@login_required
def get_worklog_events():
    logs = WorkLog.query.filter_by(user_id=current_user.id, status=1).all()

    events = []
    for log in logs:
        start_dt = datetime.combine(log.work_date, log.clock_in)
        end_dt = datetime.combine(log.work_date, log.clock_out)
        if end_dt <= start_dt:
            end_dt += timedelta(days=1)

        events.append({
            'title': f'{log.total_hours:.0f}h',
            'start': start_dt.isoformat(),
            'end': end_dt.isoformat(),
            'allDay': False
        })

    return jsonify(events)

# 근무 요약 정보 반환 (총 근무 시간)
@worklog_bp.route('/summary', methods=['GET'])
@login_required
def get_work_summary():
    try:
        # 이번 달의 첫째 날과 마지막 날 계산
        # year, month 쿼리 파라미터 처리
        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)
        now = datetime.now()
        if not year:
            year = now.year
        if not month:
            month = now.month
        first_day = datetime(year, month, 1).date()
        # 다음 달 1일 구하기
        if month == 12:
            next_month = datetime(year+1, 1, 1)
        else:
            next_month = datetime(year, month+1, 1)
        last_day = (next_month - timedelta(days=1)).date()

        # 선택한 달의 승인된 근무 기록만 필터링
        approved_logs = WorkLog.query.filter(
            WorkLog.user_id == current_user.id,
            WorkLog.status == 1,
            WorkLog.work_date >= first_day,
            WorkLog.work_date <= last_day
        ).all()

        # 총 근무 시간 계산 (저장된 total_hours 사용)
        total_hours = sum(log.total_hours for log in approved_logs)
        
        # 시급 설정 (기본값 10,030원)
        hourly_wage = 10030
        
        # 급여 계산
        total_pay = total_hours * hourly_wage
        income_tax = total_pay * 0.03  # 소득세 3%
        local_tax = total_pay * 0.003  # 지방세 0.3%
        final_pay = total_pay - income_tax - local_tax

        return jsonify({
            "total_hours": round(total_hours, 2),
            "hourly_wage": hourly_wage,
            "total_pay": int(total_pay),
            "income_tax": int(income_tax),
            "local_tax": int(local_tax),
            "final_pay": int(final_pay)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
