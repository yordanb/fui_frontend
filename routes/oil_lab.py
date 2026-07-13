from flask import Blueprint, render_template, session, redirect, url_for

oil_bp = Blueprint('oil', __name__)

@oil_bp.route('/oil-lab')
def dashboard():
    if 'token' not in session:
        return redirect(url_for('auth.login_page'))
    return render_template('oil_dashboard.html')
