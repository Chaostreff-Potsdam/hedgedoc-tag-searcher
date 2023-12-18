from flask import g

from plzidx.db import db, Tag, Pad, drop_all


def rebuild():
    drop_all()
    for uuid, content, updatedAt in g.hedgedoc.get_notes_since():
        pad = Pad(uuid=uuid, updatedAt=updatedAt)
        for tag in map(Tag.get_or_create, g.hedgedoc.extract_tags(content)):
            pad.tags.append(tag)
            db.session.add(pad)
    
    db.session.commit()


def format_pad(pad):
   return f"uuid: {pad.uuid}, title: {g.hedgedoc.get_pad_field(pad.uuid, 'title')}, alias: {g.hedgedoc.get_pad_field(pad.uuid, 'alias')}, shortid: {g.hedgedoc.get_pad_field(pad.uuid, 'shortid')}"


def dump():
    yield "<ul>"
    for tag in Tag.query.all():
        yield "<li>%s: %s</li>" % (tag.text, ", ".join(format_pad(p) for p in tag.pads))
    yield "</ul>"
