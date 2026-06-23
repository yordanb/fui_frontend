import requests
from flask import Blueprint, request, Response, current_app

api_proxy_bp = Blueprint('api_proxy', __name__)

MOBILE_API = 'http://fui-mobile-api:9090'

@api_proxy_bp.route('/api/<path:subpath>', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def proxy_api(subpath):
    url = f'{MOBILE_API}/{subpath}'
    headers = {k: v for k, v in request.headers if k.lower() not in ('host', 'content-length', 'cookie')}

    # Forward Authorization header from Flutter
    auth = request.headers.get('Authorization', '')
    if auth:
        headers['Authorization'] = auth

    try:
        r = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            params=request.args,
            json=request.get_json(silent=True) or None,
            data=request.get_data() if not request.is_json else None,
            timeout=30,
        )
        return Response(r.content, status=r.status_code, content_type=r.headers.get('content-type', 'application/json'))
    except Exception as e:
        return {'detail': str(e)}, 502
