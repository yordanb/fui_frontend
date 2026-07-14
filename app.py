import os
import logging
from datetime import timedelta
from flask import Flask, redirect, url_for, session, render_template
from flask_session import Session
from routes.auth import auth_bp
from routes.fui import fui_bp
from routes.main_routes import main_bp
from routes.oil_lab import oil_bp
from routes.dbr import dbr_bp
from routes.api_proxy import api_proxy_bp
from routes.upload import upload_bp

app = Flask(__name__)
Session(app)

# ── Production-ready config ──
app.secret_key = os.environ.get('SECRET_KEY')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = '/tmp/flask_session'
app.config['SESSION_PERMANENT'] = True

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config['SESSION_COOKIE_NAME'] = 'fui_app_session'
app.config['SESSION_COOKIE_PATH'] = '/'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_SAMESITE'] = None
app.config['SESSION_COOKIE_DOMAIN'] = None
app.config['API_BASE'] = os.environ.get('API_BASE', 'http://fui-api:8008/api')

# ── Blueprints ──
app.register_blueprint(auth_bp)
app.register_blueprint(api_proxy_bp)
app.register_blueprint(fui_bp, url_prefix='/fui')
app.register_blueprint(main_bp)
app.register_blueprint(oil_bp)
app.register_blueprint(dbr_bp)
app.register_blueprint(upload_bp)


# Security Hardening
# talisman = Talisman(app, content_security_policy=None, force_https=False, force_https_permanent=False)

# ── Logging ──
if os.environ.get('FLASK_ENV') == 'production':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
else:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S%z',
    )
    app.logger = logging.getLogger(__name__)

# ── Health Check Endpoint ──
@app.route('/health')
def health():
    return {"status": "ok", "service": "fui-frontend"}, 200

# ── Global Error Handlers ──
@app.errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

@app.route('/')
def root():
    return redirect(url_for('main.dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3005)
