from flask import g, current_app

from plzidx.db import db, Tag, Pad, drop_all


def rebuild():
    drop_all()
    for uuid, content, title, alias, shortid, updatedAt in g.hedgedoc.get_notes_since():
        pad = Pad(uuid=uuid, updatedAt=updatedAt, title=title, url=(alias or shortid))
        for tag in map(Tag.get_or_create, g.hedgedoc.extract_tags(content)):
            pad.tags.append(tag)
            db.session.add(pad)

    db.session.commit()

"""
Things that might have changed:
    1. a pad has a n new tags
    2. a pad lost tags
    3. a new pad appeared
    4. a pad was deleted
    5. a pad's plzidx tag was deleted
    6. a pad's visibility changed
    7. a pad's plzidx tag gained a password
"""

def update(last_date):
    # For now, just rebuild
    rebuild()


def format_pad(pad):
   return f"<a href=\"{current_app.config['PAD_URL'] + pad.url}\">{pad.title}</a>"

def dump():
    yield "<ul>"
    for tag in Tag.query.order_by(Tag.text).all():
        yield "<li>%s: <ul>%s</ul></li>" % (tag.text, "\n".join(f"<li>{format_pad(p)}</li>" for p in sorted(tag.pads, key=lambda p: p.title)))
    yield "</ul>"
