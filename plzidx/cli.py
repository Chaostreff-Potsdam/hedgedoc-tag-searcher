import click
from flask import Blueprint, g, current_app
from flask.cli import with_appcontext

from . import plzidx, hedgedoc, config_template

COMMAND_NAME = 'plzidx-ctrl'

bp = Blueprint(COMMAND_NAME, __name__)

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


def is_in_createconfig_mode():
    import sys
    try:
        cmdidx = sys.argv.index(COMMAND_NAME)
        return cmdidx + 1 == sys.argv.index("createconfig")
    except ValueError:
        return False


def init_cli(app):
    app.register_blueprint(bp)
