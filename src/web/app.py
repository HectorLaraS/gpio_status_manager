from flask import Flask

from src.web.routes import web_bp


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )

    app.register_blueprint(web_bp)

    return app


app = create_app()