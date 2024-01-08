import click
from flask import Blueprint, g, current_app
from flask.cli import with_appcontext

from . import plzidx, hedgedoc, config_template


bp = Blueprint('plzidx-ctrl', __name__)

def with_hedgedoc_g(a_func):

    def wrap_function(*args, **kwargs):
        g.hedgedoc = hedgedoc.Hededoc(current_app.config)
        a_func(*args, **kwargs)

    return wrap_function


@bp.cli.command('update')
@with_appcontext
@with_hedgedoc_g
def update():
    plzidx.update()


@bp.cli.command('dump')
@with_appcontext
@with_hedgedoc_g
def dump():
    print("".join(plzidx.dump()))


@bp.cli.command('createconfig')
@click.option('-o', '--output', 'output', default='-', type=click.File('w'), show_default=True)
def createconfig(output):
    print(config_template.create_config_template(), file=output)


def init_cli(app):
    app.register_blueprint(bp)
