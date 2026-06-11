import os
import logging
from flask import Flask
from flask_session import Session

# Configure logging - use INFO in production, DEBUG only when debugging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET") or os.urandom(32)

# Production session config
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours

Session(app)

# Import routes after app creation
import routes  # noqa: F401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
