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


def most_common_tags(tag_text_list, n=5):
    if not tag_text_list:
        related = Tag.get_most_common(n)
    else:
        related = Tag.get_related_tags(Tag.query.filter(Tag.text.in_(tag_text_list)).all(), n)
    
    related_t =  "\n".join(f"<li><a href=\"/{'/'.join(['pads'] + tag_text_list)}/{t.text}\">{t.text}</a></li>" for t in related)
    pads = "\n".join(f"<li>{format_pad(p)}</li>" for p in sorted(Pad.get_by_taglist(tag_text_list), key=lambda p: p.title))

    return related_t + "<hr>" + pads


def dump():
    yield "<ul>"
    for tag in Tag.query.order_by(Tag.text).all():
        yield "<li>%s: <ul>%s</ul></li>" % (tag.text, "\n".join(f"<li>{format_pad(p)}</li>" for p in sorted(tag.pads, key=lambda p: p.title)))
    yield "</ul>"
