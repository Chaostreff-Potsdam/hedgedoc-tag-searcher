import click
from flask import Blueprint, g, current_app
from flask.cli import with_appcontext

from . import config_template

COMMAND_NAME = 'plzidx-ctrl'

bp = Blueprint(COMMAND_NAME, __name__)

def with_hedgedoc_g(a_func):

    from . import hedgedoc

    def wrap_function(*args, **kwargs):
        g.hedgedoc = hedgedoc.Hededoc(current_app.config)
        a_func(*args, **kwargs)

    return wrap_function


@bp.cli.command('update')
@with_appcontext
@with_hedgedoc_g
def update():
    from . import plzidx
    plzidx.update()


@bp.cli.command('htmldump')
@with_appcontext
@with_hedgedoc_g
def htmldump():
    from . import plzidx
    print("".join(plzidx.dump()))


@bp.cli.command('dump-pad')
@click.argument('uuid')
@with_appcontext
@with_hedgedoc_g
def dump_pad(uuid):
    print(g.hedgedoc.get_pad_content(uuid))


@bp.cli.command('append-tag')
@click.argument('uuid')
@click.argument('tag')
@click.option('--dry-run', is_flag=True)
@with_appcontext
@with_hedgedoc_g
def append_tag(uuid, tag, dry_run):
    text = g.hedgedoc.append_tag(uuid, tag, dry_run)
    if dry_run and text:
        print(text)


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
