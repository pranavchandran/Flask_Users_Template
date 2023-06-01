# __Author__ = "Pranav Chandran"
# __Date__ = 27-05-2023
# __Time__ = 17:40
# __FileName__ = main.py
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from views.user_views import user_blueprint as register
from models.user import db
from Secrets.config import SECRET_KEY


app = Flask(__name__)  # Creating the flask app

app.config['SECRET_KEY'] = SECRET_KEY  # Secret key for JWT
SQLALCHEMY_DATABASE_URL = "sqlite:///./Bidapp_DB.db"  # Database URL
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URL  # Database URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # To suppress warnings
app.register_blueprint(register) # Registering the blueprint
db.init_app(app)  # Initializing the database


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()
