import os, requests
from flask import Blueprint, render_template, request, Response, session, redirect, url_for

upload_bp = Blueprint('upload', __name__)

SERVICES = {
    'oil-lab': {
        'label': '🛢 Oil Lab',
        'description': 'Upload file analisa sampel oil (.xlsx)',
        'accept': '.xlsx',
        'endpoint': '/import/xlsx',
        'method': 'POST',
        'backend': os.environ.get('OIL_API', 'http://oil-lab-api:8008'),
    },
    'dbr': {
        'label': '🔧 DBR',
        'description': 'Upload Daily Breakdown Report (.xlsx)',
        'accept': '.xlsx',
        'endpoint': '/api/v1/import/excel',
        'method': 'POST',
        'backend': os.environ.get('DBR_API', 'http://dbr-api:8010'),
    },
}


@upload_bp.route('/upload')
def upload_page():
    if 'token' not in session:
        return redirect(url_for('auth.login_page'))
    return render_template('upload.html', services=SERVICES)


@upload_bp.route('/upload-api/<service>', methods=['POST'])
def upload_proxy(service):
    if 'token' not in session:
        return {'error': 'unauthorized'}, 401

    if service not in SERVICES:
        return {'error': 'unknown service: ' + service}, 400

    svc = SERVICES[service]
    file = request.files.get('file')
    if not file:
        return {'error': 'no file uploaded'}, 400

    url = svc['backend'] + svc['endpoint']

    try:
        resp = requests.post(
            url,
            files={'file': (file.filename, file.stream, file.content_type)},
            timeout=120,
        )
        excluded = ('content-encoding', 'transfer-encoding', 'content-length', 'connection')
        resp_headers = {k: v for k, v in resp.headers.items() if k.lower() not in excluded}
        return Response(resp.content, status=resp.status_code, headers=resp_headers)
    except requests.exceptions.ConnectionError:
        return {'error': svc['label'] + ' backend unreachable'}, 502
    except Exception as e:
        return {'error': str(e)}, 500
