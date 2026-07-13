from flask import Blueprint, render_template, request, session, redirect, url_for, current_app, flash, Response, current_app as app
import requests
import json


main_bp = Blueprint('main', __name__)

def _api_get(endpoint, params=None):
    token = session.get('token')
    url = f'{current_app.config["API_BASE"]}{endpoint}'
    app.logger.info(f"API DEBUG: Calling {url} with Token: {token[:10] if token else 'NONE'}")
    headers = {'Authorization': f'Bearer {token}'}
    r = requests.get(url, headers=headers, params=params, timeout=10)
    app.logger.info(f"API DEBUG: Response {r.status_code}")
    r.raise_for_status()
    return r.json()

def _proxy_request(method, endpoint, body=None):
    token = session.get('token')
    if not token:
        return {'error': 'session expired'}, 401
    headers = {'Authorization': f'Bearer {token}'}
    if body is not None:
        headers['Content-Type'] = 'application/json'
    url = f'{current_app.config["API_BASE"]}{endpoint}'
    fn = getattr(requests, method.lower())
    if body is not None:
        r = fn(url, headers=headers, json=body, timeout=10)
    else:
        r = fn(url, headers=headers, timeout=10)
    excluded = ('content-encoding', 'transfer-encoding', 'content-length', 'connection')
    resp_headers = {k: v for k, v in r.headers.items() if k.lower() not in excluded}
    # Pastikan content-type JSON
    if 'application/json' in r.headers.get('content-type', ''):
        return Response(r.content, status=r.status_code, headers=resp_headers)
    else:
        # Force JSON response
        result = {'error': 'backend error', 'status': r.status_code, 'detail': r.text[:500]}
        return Response(json.dumps(result), status=r.status_code, content_type='application/json')

@main_bp.route('/dashboard')
def dashboard():
    app.logger.info(f"DASHBOARD DEBUG: Sesi di main_bp: {session.keys()}") 
    if 'token' not in session:
        return redirect(url_for('auth.login_page'))
    try:
        all_data = _api_get('/fui', {'size': 5})
        total = all_data.get('total', 0)
        recent = all_data.get('items', [])
        stats = {}
        for s in ['DRAFT', 'SUBMITTED', 'REVIEWED', 'APPROVED', 'EXECUTED', 'CLOSED']:
            try:
                d = _api_get('/fui', {'status': s, 'size': 1})
                stats[s] = d.get('total', 0)
            except:
                stats[s] = 0
        return render_template('dashboard.html', total=total, recent=recent, stats=stats)
    except Exception as e:
        flash(f'Error: {e}', 'error')
        return render_template('dashboard.html', total=0, recent=[], stats={})

# ─── Users page (TE/ADMIN_TE only) ───
@main_bp.route('/users')
def users():
    if 'token' not in session:
        return redirect(url_for('auth.login_page'))
    
    roles = session.get('user_roles', [])
    if 'TE' not in roles:
        flash('Akses ditolak: Hanya untuk Technical Expert', 'error')
        return redirect(url_for('main.dashboard'))
        
    try:
        data = _api_get('/users/')
        return render_template('users.html', users=data)
    except:
        flash('Failed to load users', 'error')
        return render_template('users.html', users=[])

# ─── User CRUD API proxy (TE only for write) ───
@main_bp.route('/users/api/users', methods=['GET', 'POST'])
def user_list_create():
    if 'token' not in session:
        return {'error': 'unauthorized'}, 401
    if request.method == 'GET':
        if 'TE' not in session.get('user_roles', []):
            return {'error': 'forbidden — TE role required'}, 403
        try:
            # Coba langsung ke fui-api
            token = session.get('token')
            app.logger.info(f"USERS API GET - token[:20]: {token[:20] if token else 'NONE'}...")
            headers = {'Authorization': f'Bearer {token}'}
            resp = requests.get(f'{current_app.config["API_BASE"]}/users/', headers=headers, timeout=10)
            app.logger.info(f"USERS API GET - status: {resp.status_code}")
            if resp.status_code == 401:
                return {'error': 'Token expired, please login again'}, 401
            return Response(resp.content, status=resp.status_code, content_type='application/json')
        except Exception as e:
            app.logger.error(f"USERS API GET - error: {e}")
            return {'error': str(e)}, 500
    # POST — only TE can create
    if 'TE' not in session.get('user_roles', []):
        return {'error': 'forbidden — TE role required'}, 403
    try:
        body = request.get_json(force=True)
        return _proxy_request('POST', '/users/', body)
    except Exception as e:
        return {'error': str(e)}, 500

@main_bp.route('/users/api/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
def user_detail(user_id):
    if 'token' not in session:
        return {'error': 'unauthorized'}, 401
    if request.method == 'GET':
        try:
            return _api_get(f'/users/{user_id}')
        except Exception as e:
            return {'error': str(e)}, 500
    # PUT/DELETE — only TE
    if 'TE' not in session.get('user_roles', []):
        return {'error': 'forbidden — TE role required'}, 403
    try:
        body = request.get_json(force=True) if request.method == 'PUT' else None
        return _proxy_request(request.method, f'/users/{user_id}', body)
    except Exception as e:
        return {'error': str(e)}, 500

@main_bp.route('/users/api/users/<int:user_id>/permissions', methods=['GET', 'PUT'])
def user_permissions(user_id):
    if 'token' not in session:
        return {'error': 'unauthorized'}, 401
    if 'TE' not in session.get('user_roles', []):
        return {'error': 'forbidden'}, 403
    try:
        body = request.get_json(force=True) if request.method == 'PUT' else None
        return _proxy_request(request.method, f'/users/{user_id}/permissions', body)
    except Exception as e:
        return {'error': str(e)}, 500

# ─── Equipment ───
@main_bp.route('/equipment')
def equipment():
    if 'token' not in session:
        return redirect(url_for('auth.login_page'))
    return render_template('equipment.html')

@main_bp.route('/fui-form')
def fui_form():
    if 'token' not in session:
        return redirect(url_for('auth.login_page'))
    return render_template('fui_form.html')

@main_bp.route('/fui')
def fui_list():
    if 'token' not in session:
        return redirect(url_for('auth.login_page'))
    page = request.args.get('page', 1, type=int)
    size = 20
    status = request.args.get('status', '')
    params = {'page': page, 'size': size}
    if status:
        params['status'] = status
    try:
        data = _api_get('/fui', params)
        return render_template('fui_list.html', items=data.get('items', []), total=data.get('total', 0),
                               page=page, max_page=max(1, -(-data.get('total', 0) // size)), status=status)
    except:
        flash('Failed to load FUI list', 'error')
        return render_template('fui_list.html', items=[], total=0, page=1, max_page=1, status=status)

@main_bp.route('/fui/<int:fui_id>')
def fui_detail(fui_id):
    if 'token' not in session:
        return redirect(url_for('auth.login_page'))
    try:
        fui = _api_get(f'/fui/{fui_id}')
        analyses = _api_get(f'/fui/{fui_id}/analysis')
        recs = _api_get(f'/fui/{fui_id}/recommendation')
        return render_template('fui_detail.html', fui=fui, analyses=analyses, recommendations=recs,
                               unit_number=fui.get('unit_number', ''))
    except Exception as e:
        flash(f'Error: {e}', 'error')
        return redirect(url_for('main.fui_list'))

@main_bp.route('/oil-lab')
def oil_lab():
    if 'token' not in session:
        return redirect(url_for('auth.login_page'))
    return render_template('oil_dashboard.html')


@main_bp.route('/fui-export-pdf')
def fui_export_pdf():
    cn = request.args.get('cn', '')
    if not cn: return redirect(url_for('main.fui_form'))
    
    token = session.get('token')
    headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}
    table = request.args.get('table', 'tb_lighting_eqp')
    
    try:
        eqp = requests.get(f'http://dbr-api:8010/api/v1/equipment/{table}', headers=headers).json()
        eqp = [r for r in eqp if (r.get('cn') or '').lower() == cn.lower()]
        oil = requests.get(f'http://oil-lab-api:8008/api/samples/search', headers=headers, params={'vessel': cn, 'page_size': 20}).json().get('items', [])
        dbr = requests.get(f'http://dbr-api:8010/api/v1/breakdowns', headers=headers, params={'cn': cn, 'size': 10}).json().get('items', [])
    except:
        return "Error fetching data", 500

    from weasyprint import HTML
    import io

    # Determine orientation - landscape if oil data has more than just engine
    cats = set((row.get('component') or row.get('unit_id') or 'General').strip().lower() for row in oil) if oil else set()
    orientation = 'landscape' if len(cats) > 1 else 'portrait'
    html = render_template('fui_pdf_template.html', cn=cn, eqp_data=eqp, dbr_data=dbr, oil_data=oil, orientation=orientation)
    pdf = HTML(string=html, base_url='file:///app/static/').write_pdf()
    buffer = io.BytesIO(pdf)
    buffer.seek(0)
    return Response(buffer.getvalue(), mimetype='application/pdf', headers={'Content-Disposition': f'inline; filename=FUI_{cn}.pdf'})

