import os

from flask import Flask, g

def create_app(test_config=None):
    ### App Setup

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='development',
    )

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
    def before_request():
        g.hedgedoc = app.hedgedoc

    ### Routes

    import plzidx.plzidx

    @app.route('/')
    def index():
        return 'Yes, I index'
    
    @app.route('/rebuild')
    def rebuild():
        plzidx.plzidx.rebuild()
        return 'OK'
    
    @app.route('/dump')
    def dump():
        return '\n'.join(plzidx.plzidx.dump())

    return app