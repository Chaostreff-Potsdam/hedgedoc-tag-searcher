from flask import g, current_app

from plzidx.db import db, Tag, Pad, drop_all


def pad_is_indexable(tags):
    return current_app.config['MARKER_TAG'] in tags


def rebuild():
    drop_all()
    for uuid, content, title, alias, shortid, updatedAt in g.hedgedoc.get_notes_since():
        tags = g.hedgedoc.extract_tags(content)
        if not (current_app.config['INDEX_ALL_PADS'] or pad_is_indexable(tags)):
            continue

        pad = Pad(uuid=uuid, updatedAt=updatedAt, title=title, url=(alias or shortid))
        for tag in (Tag.get_or_create(t) for t in tags if t != current_app.config['MARKER_TAG']):
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

def update(last_date=None):
    # For now, just rebuild
    rebuild()


def format_pad(pad):
   return f"<a href=\"{current_app.config['PAD_URL']}/{pad.url}\">{pad.title}</a>"


def most_common_tags(start_tag, n=5):
    t = Tag.query.filter_by(text=start_tag).first()
    return "\n".join(f"<li>{t.text}</li>" for t in Tag.get_related_tags([t], n))


def dump():
    yield "<ul>"
    for tag in Tag.query.order_by(Tag.text).all():
        yield "<li>%s: <ul>%s</ul></li>" % (tag.text, "\n".join(f"<li>{format_pad(p)}</li>" for p in sorted(tag.pads, key=lambda p: p.title)))
    yield "</ul>"
