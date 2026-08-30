from flask import Flask, jsonify, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from werkzeug.exceptions import RequestEntityTooLarge

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

    @login_manager.unauthorized_handler
    def handle_unauthorized():

        return redirect(
            url_for("main.landing")
        )

    #Importing Models    
    from app.models import User, Conversation, PDF, Message

    #Importing Blueprints
    from app.routes import auth, main, upload_bp, chat


    #Registering Blueprints
    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(upload_bp)
    app.register_blueprint(chat)

    #Prevent browser from caching application pages
    @app.after_request
    def prevent_authenticated_page_caching(response):

        response.headers["Cache-Control"] = "no-store"

        return response

    #Handling uplaod file size at Flask level
    @app.errorhandler(RequestEntityTooLarge)
    def handle_file_too_large(error):

        return jsonify({
            "success": False,
            "error_code": "FILE_TOO_LARGE"
        }), 413
    
    return app