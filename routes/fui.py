import requests
from flask import Blueprint, render_template, request, session, redirect, url_for, current_app, flash

fui_bp = Blueprint('fui', __name__)

def api_get(endpoint, params=None):
    headers = {'Authorization': f'Bearer {session["token"]}'}
    r = requests.get(f'{current_app.config["API_BASE"]}{endpoint}', headers=headers, params=params, timeout=10)
    r.raise_for_status()
    return r.json()

def api_post(endpoint, data=None):
    headers = {'Authorization': f'Bearer {session["token"]}'}
    r = requests.post(f'{current_app.config["API_BASE"]}{endpoint}', headers=headers, json=data, timeout=10)
    r.raise_for_status()
    return r.json()

@fui_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'GET':
        return render_template('fui_create.html')

    try:
        data = api_post('/fui', {
            'unit_number': request.form['unit_number'],
            'priority_level': request.form.get('priority_level', 'MEDIUM'),
        })
        flash('FUI created successfully', 'success')
        return redirect(url_for('main.fui_detail', fui_id=data['id']))
    except Exception as e:
        flash(f'Failed to create FUI: {e}', 'error')
        return render_template('fui_create.html')

@fui_bp.route('/<int:fui_id>/submit', methods=['POST'])
def submit(fui_id):
    try:
        api_post(f'/fui/{fui_id}/submit')
        flash('FUI submitted', 'success')
    except Exception as e:
        flash(f'Action failed: {e}', 'error')
    return redirect(url_for('main.fui_detail', fui_id=fui_id))

@fui_bp.route('/<int:fui_id>/<action>', methods=['POST'])
def workflow_action(fui_id, action):
    try:
        api_post(f'/fui/{fui_id}/{action}')
        flash(f'FUI {action}ed', 'success')
    except Exception as e:
        flash(f'Action failed: {e}', 'error')
    return redirect(url_for('main.fui_detail', fui_id=fui_id))

@fui_bp.route('/<int:fui_id>/analysis/create', methods=['GET', 'POST'])
def create_analysis(fui_id):
    if request.method == 'GET':
        return render_template('analysis_create.html', fui_id=fui_id)

    try:
        api_post(f'/fui/{fui_id}/analysis', {
            'analysis_type': request.form.get('analysis_type', ''),
            'problem_description': request.form['problem_description'],
            'root_cause': request.form.get('root_cause', ''),
            'impact_analysis': request.form.get('impact_analysis', ''),
            'corrective_action': request.form.get('corrective_action', ''),
        })
        flash('Analysis created', 'success')
        return redirect(url_for('main.fui_detail', fui_id=fui_id))
    except Exception as e:
        flash(f'Failed: {e}', 'error')
        return render_template('analysis_create.html', fui_id=fui_id)

@fui_bp.route('/<int:fui_id>/recommendation/create', methods=['GET', 'POST'])
def create_recommendation(fui_id):
    if request.method == 'GET':
        return render_template('rec_create.html', fui_id=fui_id)

    try:
        api_post(f'/fui/{fui_id}/recommendation', {
            'recommendation_type': request.form['recommendation_type'],
            'instruction': request.form['instruction'],
            'reason': request.form.get('reason', ''),
            'source': request.form.get('source', ''),
        })
        flash('Recommendation created', 'success')
        return redirect(url_for('main.fui_detail', fui_id=fui_id))
    except Exception as e:
        flash(f'Failed: {e}', 'error')
        return render_template('rec_create.html', fui_id=fui_id)
