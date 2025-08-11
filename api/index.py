import os
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
from app import app as flask_app

# Ensure Flask knows it's running in production on Vercel
flask_app.config["ENV"] = os.environ.get("FLASK_ENV", "production")
flask_app.config["DEBUG"] = False

# WSGI application for Vercel
# Vercel Python runtime expects a module-level variable named `app` or `handler`
app = flask_app

if __name__ == "__main__":
    # Local debug run if you `python api/index.py`
    run_simple("0.0.0.0", int(os.environ.get("PORT", 5000)), app, use_reloader=True)
