from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

base_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost:3306/ai_chats'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'database', 'ai_chats.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.secret_key = "hamdan"

CORS(app)

app.app_context().push()
db = SQLAlchemy(app)


flashes = {
    "info": "blue",
    "success": "teal",
    "danger": "red",
    "warning": "yellow",
    "primary": "bg-gray-100 border border-gray-200 text-sm text-gray-800 rounded-lg p-4 dark:bg-white/10 dark:border-white/20 dark:text-white",
    "secondary": "bg-gray-50 border border-gray-200 text-sm text-gray-600 rounded-lg p-4 dark:bg-white/[.05] dark:border-white/10 dark:text-gray-400"
}