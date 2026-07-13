from flask import Blueprint, render_template, session, redirect, url_for

dbr_bp = Blueprint('dbr', __name__)

@dbr_bp.route('/dbr')
def dashboard():
    if 'token' not in session:
        return redirect(url_for('auth.login_page'))
    return render_template('dbr_dashboard.html')
