import requests
from flask import Blueprint, render_template, request, Response, session, redirect, url_for

dbr_bp = Blueprint('dbr', __name__)

import os
DBR_API = os.environ.get('DBR_API', 'http://localhost:8010')

@dbr_bp.route('/dbr')
def dashboard():
    if 'token' not in session:
        return redirect(url_for('auth.login_page'))
    return render_template('dbr_dashboard.html')

@dbr_bp.route('/dbr-api/<path:subpath>', methods=['GET', 'POST', 'DELETE'])
def proxy(subpath):
    if 'token' not in session:
        return {'error': 'unauthorized'}, 401

    # Role check: only TE can truncate
    if subpath == 'api/v1/breakdowns/truncate':
        user_roles = session.get('user', {}).get('roles', [])
        if 'TE' not in user_roles:
            return {'error': 'forbidden — TE role required'}, 403

    url = f'{DBR_API}/{subpath}'
    if request.query_string:
        url += f'?{request.query_string.decode()}'

    method = request.method.lower()
    fn = getattr(requests, method)
    headers = {'Authorization': f'Bearer {session.get("token")}', 'Accept': 'application/json'}

    try:
        if method == 'get':
            resp = fn(url, headers=headers, params=request.args, timeout=30)
        elif method == 'delete':
            resp = fn(url, headers=headers, timeout=30)
        else:
            # Forward Content-Type
            if request.content_type:
                headers['Content-Type'] = request.content_type
            resp = fn(url, headers=headers, data=request.get_data(), timeout=90)

        excluded = ('content-encoding', 'transfer-encoding', 'content-length', 'connection')
        resp_headers = {k: v for k, v in resp.headers.items() if k.lower() not in excluded}

        return Response(resp.content, status=resp.status_code, headers=resp_headers)
    except requests.exceptions.ConnectionError:
        return {'error': 'DBR backend unreachable'}, 502
    except Exception as e:
        return {'error': str(e)}, 500
