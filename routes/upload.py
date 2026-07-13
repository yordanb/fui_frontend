from flask import Blueprint, render_template, request, jsonify
import requests, os

OIL_API = 'http://oil-lab-api:8008'

upload_bp = Blueprint('upload', __name__)

SERVICES = {
    'oil': {
        'label': 'Oil Lab',
        'description': 'Upload sampel minyak lab',
        'accept': '.xlsx, .csv',
        'endpoint': '/api/upload-file'
    },
    'dbr': {
        'label': 'DBR',
        'description': 'Upload data DBR',
        'accept': '.xlsx, .csv',
        'endpoint': '/api/upload-dbr'
    },
    'files': {
        'label': 'Files',
        'description': 'Upload file ke server',
        'accept': '*',
        'endpoint': '/api/upload-local'
    }
}

@upload_bp.route('/upload', methods=['GET'])
def upload_page():
    return render_template('upload.html', services=SERVICES)

@upload_bp.route('/api/upload-file', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if not file: return jsonify({'error': 'No file'}), 400
    try:
        endpoint = f'{OIL_API}/api/import/xlsx'
        if file.filename.endswith('.csv'):
            endpoint = f'{OIL_API}/api/dbr/import-csv'
        resp = requests.post(endpoint, files={'file': (file.filename, file.read(), file.content_type)}, timeout=300)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@upload_bp.route('/api/import/status/<task_id>', methods=['GET'])
def import_status(task_id):
    try:
        resp = requests.get(f'{OIL_API}/api/import/status/{task_id}', timeout=30)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@upload_bp.route('/api/database/truncate', methods=['POST'])
def truncate_db():
    try:
        resp = requests.post(f'{OIL_API}/api/import/truncate', timeout=30)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@upload_bp.route('/api/upload-dbr', methods=['POST'])
def upload_dbr():
    file = request.files.get('file')
    if not file: return jsonify({'error': 'No file'}), 400
    try:
        endpoint = f'http://dbr-api:8010/api/v1/import/excel'
        if file.filename.endswith('.csv'):
            endpoint = f'http://dbr-api:8010/api/v1/import/import-csv'
        resp = requests.post(endpoint, files={'file': (file.filename, file.read(), file.content_type)}, timeout=600)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@upload_bp.route('/api/database/truncate/dbr', methods=['DELETE'])
def truncate_dbr_db():
    try:
        resp = requests.delete(f'http://dbr-api:8010/api/v1/breakdowns/truncate', timeout=30)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@upload_bp.route('/api/upload-local', methods=['POST'])
def upload_local():
    file = request.files.get('file')
    if not file: return jsonify({'error': 'No file'}), 400
    save_path = '/app/uploads'
    os.makedirs(save_path, exist_ok=True)
    file.save(os.path.join(save_path, file.filename))
    return jsonify({'status': 'success', 'message': f'File {file.filename} saved to {save_path}'}), 200
