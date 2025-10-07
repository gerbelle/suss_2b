from flask import Flask
from flask_mongoengine import MongoEngine
from flask_login import LoginManager

db = MongoEngine()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    # Set a secret key for session management. This is required to use sessions.
    # In a real-world application, this should be a complex, randomly generated string.
    app.secret_key = 'your_super_secret_key_here'
    app.config['MONGODB_SETTINGS'] = {
        'db' : 'BookStoreDB',
        'host': 'localhost',
        'port': 27017
    }

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login' #The name of the view function for the login page
    
    

    return app

app = create_app()    

from app.model import User
@login_manager.user_loader
def load_user(user_id):
    return User.objects(id=user_id).first()