from flask import Flask
from rolesaver import app

web_app = Flask(__name__)

web_app = app(web_app)
web_app.run('0.0.0.0', port=5544)
