import os

from flask import Flask, g

def create_app(test_config=None):
    ### App Setup

    from . import config_template
    from . import cli

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(config_template.default_config)

    if test_config is not None:
        app.config.from_mapping(test_config)
    elif app.config.from_envvar(config_template.config_env_var_name, silent=True):
        pass
    elif app.config.from_pyfile('config.py', silent=True):
        pass
    elif cli.is_in_createconfig_mode():
        cli.init_cli(app)
        return app
    else:
        raise RuntimeError(f"Unable to load configuration file. Expected '{os.path.join(app.instance_path, 'config.py')}' or setting envvar {config_template.config_env_var_name} (absolute or relative to instance_path)")

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    ### Components Setup

    from . import db
    db.init_db(app)

    cli.init_cli(app)

    @app.before_request
    @cli.with_hedgedoc_g
    def before_request():
        pass

    ### Routes

    from . import views
    app.register_blueprint(views.bp)

    return app