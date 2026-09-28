#!/usr/bin/env python3
"""Run the Leafletang Enterprises public website."""
import os

# Vercel sets VERCEL=1 — force production config
if os.environ.get('VERCEL'):
    os.environ.setdefault('FLASK_ENV', 'production')

from app import create_app

app = create_app(os.environ.get('FLASK_ENV', 'development'))

# Vercel / WSGI entry
application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_ENV') == 'development')
