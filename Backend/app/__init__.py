from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Load environment variables
    load_dotenv()
    
    # Configure app
    app.config['GITHUB_TOKEN'] = os.getenv('GITHUB_TOKEN')
    app.config['HUGGINGFACE_TOKEN'] = os.getenv('HUGGINGFACE_TOKEN')
    
    # Register blueprints
    from .routes import main
    app.register_blueprint(main)
    
    return app 