import os
from flask import Flask, redirect, url_for
from routes.auth import auth_bp
from routes.fui import fui_bp
from routes.main_routes import main_bp
from routes.oil_lab import oil_bp
from routes.dbr import dbr_bp

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fui-secret-key-change-me')
app.config['API_BASE'] = os.environ.get('API_BASE', 'http://localhost:8008/api')  # FUI API
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # HTTP tunnel

app.register_blueprint(auth_bp)
app.register_blueprint(fui_bp, url_prefix='/fui')
app.register_blueprint(main_bp)
app.register_blueprint(oil_bp)
app.register_blueprint(dbr_bp)


@app.route('/')
def root():
    return redirect(url_for('main.dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3005, debug=True, use_reloader=False)
