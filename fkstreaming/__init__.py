import os
from flask import Flask
from flask_restful import Api
from flask import render_template
from fkstreaming.home.home import home
from fkstreaming.api.api import content_v1
from fkstreaming.home.player import player


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    # register blueprints
    #app.register_blueprint(get_video, url_prefix='/api')
    #app.register_blueprint(find_content, url_prefix='/api')
    app.register_blueprint(player)
    app.register_blueprint(home)

    app.register_blueprint(content_v1, url_prefix='/api/v1/') # register api

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html')
         
    return app