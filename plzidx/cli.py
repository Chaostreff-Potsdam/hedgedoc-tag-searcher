import click
from flask import Blueprint, g, current_app
from flask.cli import with_appcontext

from . import plzidx, hedgedoc


bp = Blueprint('worker', __name__)

def with_hedgedoc_g(a_func):

    def wrap_function(*args, **kwargs):
        g.hedgedoc = hedgedoc.Hededoc(current_app.config)
        a_func(*args, **kwargs)

    return wrap_function


@bp.cli.command('update')
@with_appcontext
@with_hedgedoc_g
def update():
    plzidx.rebuild()


@bp.cli.command('dump')
@with_appcontext
@with_hedgedoc_g
def dump():
    print("".join(plzidx.dump()))


def init_cli(app):
    app.register_blueprint(bp)
