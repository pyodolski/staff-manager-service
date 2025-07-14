from flask import jsonify, request
from flask_login import login_required, current_user
from .models import User, WorkLog
from .admin_api import admin_bp

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
    from datetime import datetime
    start = request.args.get('start')
    end = request.args.get('end')
    try:
        start_date = datetime.strptime(start, '%Y-%m-%d').date()
        end_date = datetime.strptime(end, '%Y-%m-%d').date()
    except:
        return jsonify([])
    logs = WorkLog.query.filter(
        WorkLog.user_id == user_id,
        WorkLog.status == 1,
        WorkLog.work_date >= start_date,
        WorkLog.work_date <= end_date
    ).all()
    events = []
    for log in logs:
        events.append({
            'title': f"{round(log.total_hours,2)}시간",
            'start': log.work_date.strftime('%Y-%m-%d'),
            'allDay': True
        })
    return jsonify(events)
