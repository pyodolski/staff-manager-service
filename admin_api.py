from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import db, WorkLog, User

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# 미승인 근무 목록 조회
@admin_bp.route('/pending_worklogs', methods=['GET'])
@login_required
def pending_worklogs():
    if not hasattr(current_user, 'role') or current_user.role != 1:
        return jsonify({'error': '권한 없음'}), 403
    logs = WorkLog.query.filter_by(status=0).order_by(WorkLog.work_date.desc()).all()
    result = []
    for log in logs:
        user = User.query.get(log.user_id)
        result.append({
            'id': log.id,
            'name': user.name if user else '-',
            'work_date': log.work_date.strftime('%Y-%m-%d'),
            'clock_in': log.clock_in.strftime('%H:%M'),
            'clock_out': log.clock_out.strftime('%H:%M'),
            'total_hours': round(log.total_hours, 2),
            'status': log.status
        })
    return jsonify(result)

# 근무 승인
@admin_bp.route('/approve_worklog', methods=['POST'])
@login_required
def approve_worklog():
    if not hasattr(current_user, 'role') or current_user.role != 1:
        return jsonify({'error': '권한 없음'}), 403
    log_id = request.json.get('id')
    log = WorkLog.query.get(log_id)
    if log and log.status == 0:
        log.status = 1
        db.session.commit()
        return jsonify({'message': '승인 완료'})
    return jsonify({'error': '잘못된 요청'}), 400

# 근무 거절
@admin_bp.route('/reject_worklog', methods=['POST'])
@login_required
def reject_worklog():
    if not hasattr(current_user, 'role') or current_user.role != 1:
        return jsonify({'error': '권한 없음'}), 403
    log_id = request.json.get('id')
    log = WorkLog.query.get(log_id)
    if log and log.status == 0:
        log.status = -1
        db.session.commit()
        return jsonify({'message': '거절 완료'})
    return jsonify({'error': '잘못된 요청'}), 400

# 직원별 월별/누적 근무시간 및 급여 합계 조회
@admin_bp.route('/staff_summary', methods=['GET'])
@login_required
def staff_summary():
    if not hasattr(current_user, 'role') or current_user.role != 1:
        return jsonify({'error': '권한 없음'}), 403
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    from datetime import datetime, timedelta
    now = datetime.now()
    if not year:
        year = now.year
    if not month:
        month = now.month
    first_day = datetime(year, month, 1).date()
    if month == 12:
        next_month = datetime(year+1, 1, 1)
    else:
        next_month = datetime(year, month+1, 1)
    last_day = (next_month - timedelta(days=1)).date()

    users = User.query.all()
    hourly_wage = 10030
    result = []
    for user in users:
        if user.id == current_user.id:
            continue
        # 월별 승인 근무
        monthly_logs = WorkLog.query.filter(
            WorkLog.user_id == user.id,
            WorkLog.status == 1,
            WorkLog.work_date >= first_day,
            WorkLog.work_date <= last_day
        ).all()
        monthly_hours = sum(log.total_hours for log in monthly_logs)
        monthly_pay = monthly_hours * hourly_wage
        monthly_income_tax = monthly_pay * 0.03
        monthly_local_tax = monthly_pay * 0.003
        monthly_final_pay = monthly_pay - monthly_income_tax - monthly_local_tax
        # 누적 승인 근무
        cumulative_logs = WorkLog.query.filter(
            WorkLog.user_id == user.id,
            WorkLog.status == 1
        ).all()
        cumulative_hours = sum(log.total_hours for log in cumulative_logs)
        cumulative_pay = cumulative_hours * hourly_wage
        cumulative_income_tax = cumulative_pay * 0.03
        cumulative_local_tax = cumulative_pay * 0.003
        cumulative_final_pay = cumulative_pay - cumulative_income_tax - cumulative_local_tax
        result.append({
            'user_id': user.id,
            'name': user.name,
            'email': user.email,
            'monthly_hours': round(monthly_hours, 2),
            'monthly_final_pay': int(monthly_final_pay),
            'cumulative_hours': round(cumulative_hours, 2),
            'cumulative_final_pay': int(cumulative_final_pay)
        })
    return jsonify(result)

# 관리자용 직원별 월간 근무기록 리스트 조회
@admin_bp.route('/staff_worklog_list/<int:user_id>', methods=['GET'])
@login_required
def staff_worklog_list(user_id):
    if not hasattr(current_user, 'role') or current_user.role != 1:
        return jsonify({'error': '권한 없음'}), 403
    from datetime import datetime
    year = int(request.args.get('year'))
    month = int(request.args.get('month'))
    start_date = datetime(year, month, 1).date()
    if month == 12:
        end_date = datetime(year+1, 1, 1).date()
    else:
        end_date = datetime(year, month+1, 1).date()
    logs = WorkLog.query.filter(
        WorkLog.user_id == user_id,
        WorkLog.work_date >= start_date,
        WorkLog.work_date < end_date
    ).order_by(WorkLog.work_date).all()
    result = []
    for log in logs:
        result.append({
            'id': log.id,
            'work_date': log.work_date.strftime('%Y-%m-%d'),
            'clock_in': log.clock_in.strftime('%H:%M') if log.clock_in else '',
            'clock_out': log.clock_out.strftime('%H:%M') if log.clock_out else '',
            'total_hours': round(log.total_hours, 2) if log.total_hours is not None else '',
            'status': log.status,  # 1: 승인, 0: 미승인 등
        })
    return jsonify(result)

# 관리자용 직원 단일 정보 조회
@admin_bp.route('/staff_info/<int:user_id>', methods=['GET'])
@login_required
def staff_info(user_id):
    if not hasattr(current_user, 'role') or current_user.role != 1:
        return jsonify({'error': '권한 없음'}), 403
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': '사용자 없음'}), 404
    return jsonify({'user_id': user.id, 'name': user.name, 'email': user.email})

# 관리자용 직원별 승인 근무 이벤트 조회 (FullCalendar용)
@admin_bp.route('/staff_worklog_events/<int:user_id>', methods=['GET'])
@login_required
def staff_worklog_events(user_id):
    if not hasattr(current_user, 'role') or current_user.role != 1:
        return jsonify({'error': '권한 없음'}), 403
    from datetime import datetime, timedelta
    start = request.args.get('start')
    end = request.args.get('end')
    from dateutil.parser import parse as dateparse
    try:
        start_date = dateparse(start).date()
        end_date = dateparse(end).date()
    except Exception as e:
        print("date parse error:", e)
        return jsonify([])
    logs = WorkLog.query.filter(
        WorkLog.user_id == user_id,
        WorkLog.status == 1,
        WorkLog.work_date >= start_date,
        WorkLog.work_date <= end_date
    ).all()
    events = []
    for log in logs:
        start_dt = datetime.combine(log.work_date, log.clock_in)
        end_dt = datetime.combine(log.work_date, log.clock_out)
        if end_dt <= start_dt:
            end_dt += timedelta(days=1)
        events.append({
            'title': f"{round(log.total_hours,2)}시간",
            'start': start_dt.isoformat(),
            'end': end_dt.isoformat(),
            'allDay': False
        })
    return jsonify(events)

# 관리자용 근무기록 삭제
@admin_bp.route('/delete_worklog/<int:worklog_id>', methods=['DELETE'])
@login_required
def delete_worklog(worklog_id):
    if not hasattr(current_user, 'role') or current_user.role != 1:
        return jsonify({'error': '권한 없음'}), 403
    log = WorkLog.query.get(worklog_id)
    if not log:
        return jsonify({'error': '근무기록 없음'}), 404
    db.session.delete(log)
    db.session.commit()
    return jsonify({'result': 'ok'})

# 관리자용 근무기록 수정
@admin_bp.route('/update_worklog/<int:worklog_id>', methods=['POST'])
@login_required
def update_worklog(worklog_id):
    if not hasattr(current_user, 'role') or current_user.role != 1:
        return jsonify({'error': '권한 없음'}), 403
    log = WorkLog.query.get(worklog_id)
    if not log:
        return jsonify({'error': '근무기록 없음'}), 404
    data = request.json
    from datetime import datetime
    try:
        if 'clock_in' in data:
            log.clock_in = datetime.strptime(data['clock_in'], '%H:%M').time() if data['clock_in'] else None
        if 'clock_out' in data:
            log.clock_out = datetime.strptime(data['clock_out'], '%H:%M').time() if data['clock_out'] else None
        if 'total_hours' in data:
            log.total_hours = float(data['total_hours']) if data['total_hours'] else None
        if 'status' in data:
            log.status = int(data['status'])
        db.session.commit()
        return jsonify({'result': 'ok'})
    except Exception as e:
        return jsonify({'error': f'수정 오류: {e}'})

# 관리자용 근무기록 추가
@admin_bp.route('/add_worklog/<int:user_id>', methods=['POST'])
@login_required
def add_worklog(user_id):
    if not hasattr(current_user, 'role') or current_user.role != 1:
        return jsonify({'error': '권한 없음'}), 403
    data = request.json
    from datetime import datetime
    try:
        work_date = datetime.strptime(data['work_date'], '%Y-%m-%d').date()
        clock_in = datetime.strptime(data['clock_in'], '%H:%M').time() if data['clock_in'] else None
        clock_out = datetime.strptime(data['clock_out'], '%H:%M').time() if data['clock_out'] else None
        total_hours = float(data['total_hours']) if data['total_hours'] else 0
        log = WorkLog(
            user_id=user_id,
            work_date=work_date,
            clock_in=clock_in,
            clock_out=clock_out,
            total_hours=total_hours,
            status=1  # 관리자 추가는 무조건 승인
        )
        db.session.add(log)
        db.session.commit()
        return jsonify({'result': 'ok'})
    except Exception as e:
        return jsonify({'error': f'추가 오류: {e}'})
