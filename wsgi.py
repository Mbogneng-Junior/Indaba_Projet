"""WSGI entry point for the Dash application"""
import os
import sys

# Ajouter le répertoire courant au PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from app import server as application

# Pour Gunicorn
app = application

if __name__ == '__main__':
    app.run()
