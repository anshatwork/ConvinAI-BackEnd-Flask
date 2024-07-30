from flask import Flask
from flask_pymongo import PyMongo
from flask_marshmallow import Marshmallow
import os

mongo = PyMongo()
ma = Marshmallow()

def create_app():
    app = Flask(__name__)
    
    # Load configurations directly
    app.config['MONGO_URI'] = 'mongodb://localhost:27017/anshop'
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    app.config['SECRET_KEY'] = '1234'  # Set a secret key for session management and other uses
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit upload size to 16 MB

    # Initialize Flask extensions
    mongo.init_app(app)
    ma.init_app(app)
    
    # Register blueprints or import routes and models here
    
    from app.view import view
    from app import model
    app.register_blueprint(view)
    
    
    return app
