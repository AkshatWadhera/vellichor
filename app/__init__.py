from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

#User Loader
@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)

    app.config.from_object("config.Config")

    #Initializing db, login_manager and migrations
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    #Importing Blueprints
    from app.models import User, Conversation, PDF, Message
    from app.routes import auth, main

    #Registering Blueprints
    app.register_blueprint(auth)
    app.register_blueprint(main)

    return app