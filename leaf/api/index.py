"""Optional Vercel serverless entry — imports the Flask app."""
import os
os.environ.setdefault('FLASK_ENV', 'production')

from run import app  # noqa: F401 — Vercel looks for `app`
