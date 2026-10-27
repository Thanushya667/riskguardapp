
import os

# ---------------------------------------------------------
# Local Google OAuth development setting
# ---------------------------------------------------------
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

from dotenv import load_dotenv
from flask import Flask, send_from_directory
from config import Config
from database import db
from flask_mail import Mail

from routes import (
    auth_bp,
    student_bp,
    prediction_bp,
    alert_bp,
    statistics_bp,
    faculty_bp,
    classroom_bp,
    dataset_bp,
    intervention_bp
)


# ---------------------------------------------------------
# Load Environment Variables
# ---------------------------------------------------------
load_dotenv()


# ---------------------------------------------------------
# Flask-Mail
# ---------------------------------------------------------
mail = Mail()


# ---------------------------------------------------------
# Google Classroom Configuration Check
# ---------------------------------------------------------
print("GOOGLE CLIENT ID:", Config.GOOGLE_CLIENT_ID)
print("GOOGLE SECRET EXISTS:", bool(Config.GOOGLE_CLIENT_SECRET))
print("GOOGLE REDIRECT URI:", Config.GOOGLE_REDIRECT_URI)


# ---------------------------------------------------------
# Create Flask Application
# ---------------------------------------------------------
def create_app():

    app = Flask(
        __name__,
        static_folder=Config.STATIC_FOLDER,
        static_url_path="/static",
        template_folder=Config.TEMPLATE_FOLDER
    )

    app.config.from_object(Config)

    # -----------------------------------------------------
    # Session Configuration
    # -----------------------------------------------------
    app.secret_key = Config.SECRET_KEY
    app.config["SESSION_COOKIE_SECURE"] = False
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # -----------------------------------------------------
    # Gmail SMTP Configuration
    # -----------------------------------------------------
    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 587
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")

    # -----------------------------------------------------
    # Initialize Database
    # -----------------------------------------------------
    db.init_app(app)

    with app.app_context():
        # Creates missing tables; does not migrate existing tables.
        db.create_all()

    # -----------------------------------------------------
    # Initialize Mail
    # -----------------------------------------------------
    mail.init_app(app)

    # -----------------------------------------------------
    # Register Existing API Blueprints
    # -----------------------------------------------------
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(prediction_bp)
    app.register_blueprint(alert_bp)
    app.register_blueprint(statistics_bp)
    app.register_blueprint(faculty_bp)
    app.register_blueprint(classroom_bp)
    app.register_blueprint(dataset_bp)
    app.register_blueprint(intervention_bp)

    # -----------------------------------------------------
    # CORS Headers
    # -----------------------------------------------------
    @app.after_request
    def add_response_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = (
            "Content-Type,Authorization"
        )
        response.headers["Access-Control-Allow-Methods"] = (
            "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    # -----------------------------------------------------
    # Serve Frontend and Static Files
    # -----------------------------------------------------
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_frontend(path):

        # Let Flask serve files from frontend/static.
        # Example: /static/js/app.js
        if path.startswith("static/"):
            file_path = os.path.join(
                app.static_folder,
                path[len("static/"):]
            )

            if os.path.isfile(file_path):
                return send_from_directory(
                    app.static_folder,
                    path[len("static/"):]
                )

            return "Static file not found: " + path, 404

        # Support /js/app.js and /css/style.css URLs too.
        if path.startswith(("js/", "css/", "images/")):
            file_path = os.path.join(app.static_folder, path)

            if os.path.isfile(file_path):
                return send_from_directory(
                    app.static_folder,
                    path
                )

            return "Static file not found: " + path, 404

        # If the requested path is a real frontend asset,
        # serve that file rather than index.html.
        file_path = os.path.join(app.static_folder, path)

        if path and os.path.isfile(file_path):
            return send_from_directory(
                app.static_folder,
                path
            )

        # Serve the React application page.
        return send_from_directory(
            app.template_folder,
            "index.html"
        )

    # -----------------------------------------------------
    # Handle 404 Errors
    # -----------------------------------------------------
    @app.errorhandler(404)
    def not_found(error):
        return "Page not found", 404

    return app


# ---------------------------------------------------------
# Create Application
# ---------------------------------------------------------
app = create_app()


# ---------------------------------------------------------
# Run Flask Server
# ---------------------------------------------------------
if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    print(
        f"RiskGuard Server starting on http://127.0.0.1:{port}"
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )
