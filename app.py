import os
import logging
from datetime import timedelta
from flask import Flask, redirect, url_for, session
from routes.auth import auth_bp
from routes.fui import fui_bp
from routes.main_routes import main_bp
from routes.oil_lab import oil_bp
from routes.dbr import dbr_bp
from routes.api_proxy import api_proxy_bp
from routes.upload import upload_bp

app = Flask(__name__)

# ── Logging ──
if os.environ.get('FLASK_ENV') == 'production':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
else:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

# ── Production-ready config ──
app.secret_key = os.environ.get('SECRET_KEY')
if not app.secret_key:
    raise RuntimeError('SECRET_KEY environment variable is required')

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config['API_BASE'] = os.environ.get('API_BASE', 'http://fui-api:8008/api')
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True

app.register_blueprint(auth_bp)
app.register_blueprint(fui_bp, url_prefix='/fui')
app.register_blueprint(main_bp)
app.register_blueprint(oil_bp)
app.register_blueprint(dbr_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(api_proxy_bp)

@app.route('/')
def root():
    return redirect(url_for('main.dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3005)
