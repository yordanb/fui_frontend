import requests
from flask import Blueprint, render_template, request, session, redirect, url_for, current_app, flash, current_app as app, current_app as app

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form.get('username')
    password = request.form.get('password')

    try:
        r = requests.post(f'{current_app.config["API_BASE"]}/auth/login',
                          json={'username': username, 'password': password}, timeout=10)
        if r.status_code != 200:
            flash('Invalid username or password', 'error')
            return render_template('login.html')

        data = r.json()
        session.clear() # Bersihin total
        session['token'] = data['access_token']
        session.permanent = True

        me = requests.get(f'{current_app.config["API_BASE"]}/auth/me',
                          headers={'Authorization': f'Bearer {data["access_token"]}'}, timeout=10)
        
        # Simpan cuma nama/role, jangan object gede
        u = me.json()
        session['user_nama'] = u.get('fullname', u.get('username', 'User'))
        session['user_roles'] = u.get('roles', [])
        app.logger.info(f"USER DATA: {u}"); app.logger.info(f"SESSION ROLES: {u.get('roles', [])}")

        app.logger.info(f"LOGIN SUKSES! Sesi: {session.keys()}")
        return redirect(url_for('main.dashboard'))
    except Exception as e:
        flash(f'Connection error: {e}', 'error')
        return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login_page'))
