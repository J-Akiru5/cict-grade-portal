"""
Vercel serverless entrypoint.
All requests are routed here via vercel.json.
"""
import sys
import os

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app

app = create_app('production')

# Vercel expects the WSGI app to be named `app`
