from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret!'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://tic_user:Bgzcm3mEzunzP8K227xKqcY6tCiXLbIk@dpg-cp7kcnmd3nmc73btcp90-a.oregon-postgres.render.com/tic'

    db.init_app(app)

    with app.app_context():
        db.create_all()

    return app
