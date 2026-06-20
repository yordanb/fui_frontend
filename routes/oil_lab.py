import requests
from flask import Blueprint, render_template, request, Response, current_app, session, redirect, url_for

oil_bp = Blueprint('oil', __name__)

import os
OIL_API = os.environ.get('OIL_API', 'http://localhost:8009')

@oil_bp.route('/oil-lab')
def dashboard():
    if 'token' not in session:
        return redirect(url_for('auth.login_page'))
    return render_template('oil_dashboard.html')

@oil_bp.route('/oil-lab-api/<path:subpath>', methods=['GET', 'POST', 'DELETE'])
def proxy(subpath):
    if 'token' not in session:
        return {'error': 'unauthorized'}, 401

    url = f'{OIL_API}/{subpath}'
    if request.query_string:
        url += f'?{request.query_string.decode()}'

    method = request.method.lower()
    fn = getattr(requests, method)

    try:
        if method == 'get':
            resp = fn(url, headers={'Accept': 'application/json'}, params=request.args, timeout=30)
        elif method == 'delete':
            resp = fn(url, headers={'Accept': 'application/json'}, timeout=30)
        else:
            resp = fn(url, headers={'Accept': 'application/json'}, data=request.get_data(), timeout=30)

        excluded = ('content-encoding', 'transfer-encoding', 'content-length', 'connection')
        resp_headers = {k: v for k, v in resp.headers.items() if k.lower() not in excluded}

        return Response(
            resp.content,
            status=resp.status_code,
            headers=resp_headers
        )
    except requests.exceptions.ConnectionError:
        return {'error': 'Oil Lab backend unreachable'}, 502
    except Exception as e:
        return {'error': str(e)}, 500
