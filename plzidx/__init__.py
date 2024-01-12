import os

from flask import Flask, g

def create_app(test_config=None):
    ### App Setup

    from . import config_template

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(config_template.default_config)

    if test_config is None:
        app.config.from_pyfile('config.py', silent=False)
    else:    
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    ### Components Setup

    from . import db
    db.init_db(app)

    from . import cli
    cli.init_cli(app)

    @app.before_request
    @cli.with_hedgedoc_g
    def before_request():
        pass

    ### Routes

    from . import views
    app.register_blueprint(views.bp)

    return app