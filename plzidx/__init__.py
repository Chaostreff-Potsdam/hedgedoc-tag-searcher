import os

from flask import Flask

import plzidx.hedgedocdb

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

    hedgedoc = plzidx.hedgedocdb.HededocDB(app.config)

    ### Routes

    @app.route('/')
    def index():
        return 'Yes, I index'
    
    @app.route('/hdtest')
    def hdtest():
        return '<br />'.join("%s: %r" % t for t in plzidx.hedgedocdb.test(hedgedoc, None))

    return app