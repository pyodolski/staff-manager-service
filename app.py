import os
from datetime import timedelta
from flask import Flask
from flask_session import Session
from config import Config
from models import db
from auth import auth_bp, google_bp
from worklog_api import worklog_bp
from flask_login import LoginManager
app = Flask(__name__)
app.config.from_object(Config)

# 세션 설정
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
Session(app)

db.init_app(app)

with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)

from models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(auth_bp)
app.register_blueprint(google_bp, url_prefix='/login')
app.register_blueprint(worklog_bp)
from admin_api import admin_bp
app.register_blueprint(admin_bp)
from flask_login import current_user, login_required
from flask import render_template, redirect, url_for
@app.route('/admin')
@login_required
def admin_page():
    if not hasattr(current_user, 'role') or current_user.role != 1:
        return redirect(url_for('index'))
    return render_template('admin.html')

@app.route('/admin/staff_list')
@login_required
def staff_list_page():
    if not hasattr(current_user, 'role') or current_user.role != 1:
        return redirect(url_for('index'))
    return render_template('staff_list.html')

@app.route('/admin/staff_detail/<int:user_id>')
@login_required
def staff_detail(user_id):
    if not hasattr(current_user, 'role') or current_user.role != 1:
        return redirect(url_for('login'))
    return render_template('staff_detail.html')

@app.route('/admin/payslip/<int:user_id>')
@login_required
def payslip(user_id):
    if not hasattr(current_user, 'role') or current_user.role != 1:
        return redirect(url_for('login'))
    return render_template('payslip.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
