import requests
import logging
from flask import Blueprint, request, Response, session

api_proxy_bp = Blueprint('api_proxy', __name__)
logger = logging.getLogger(__name__)

SERVICES = {
    'api': 'http://fui-api:8008',
    'oil-lab-api': 'http://oil-lab-api:8008',
    'dbr-api': 'http://dbr-api:8010'
}

@api_proxy_bp.route('/<service>/<path:subpath>', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def proxy_service(service, subpath):
    if service not in SERVICES: 
        return {'detail': 'Service not found'}, 404
    
    url = f"{SERVICES[service]}/{subpath}"
    logger.info(f"PROXY: {request.method} {url}")
    
    # Minimal headers - hanya forward Accept
    fwd_headers = {
        'Accept': request.headers.get('Accept', '*/*'),
        'User-Agent': 'fui-proxy/1.0'
    }
    
    # Token hanya untuk service 'api'
    token = session.get('token')
    if token and service == 'api':
        fwd_headers['Authorization'] = f'Bearer {token}'
    
    try:
        # Kirim method & params saja, tanpa data/cookies/body
        r = requests.request(
            method=request.method,
            url=url,
            headers=fwd_headers,
            params=request.args,
            timeout=60
        )
        # Hapus header transfer-encoding/chunked dari response backend
        resp_headers = dict(r.headers)
        resp_headers.pop('Transfer-Encoding', None)
        resp_headers.pop('Content-Encoding', None)
        
        return Response(
            r.content,
            status=r.status_code,
            headers=resp_headers
        )
    except requests.exceptions.ConnectionError:
        logger.error(f"PROXY CONNECTION REFUSED: {url}")
        return {'error': 'Oil Lab backend unreachable - connection refused'}, 502
    except requests.exceptions.Timeout:
        logger.error(f"PROXY TIMEOUT: {url}")
        return {'error': 'Oil Lab backend unreachable - timeout'}, 502
    except Exception as e:
        logger.error(f"PROXY ERROR: {e}")
        return {'error': 'Oil Lab backend unreachable'}, 502
