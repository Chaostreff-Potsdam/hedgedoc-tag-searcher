from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, ForeignKeyConstraint, func
from typing import List
from sqlalchemy.orm import declarative_base, mapped_column, relationship, Mapped

import datetime

Base = declarative_base()

db = SQLAlchemy(model_class=Base)


def init_db(app):
    with app.app_context():
        db.init_app(app)
        db.create_all()


association_table = Table(
    'association',
    Base.metadata,
    Column('tag_id', ForeignKey('tag.id'), primary_key=True),
    Column('pad_uuid', ForeignKey('pad.uuid'), primary_key=True),
    ForeignKeyConstraint(['tag_id'], ['tag.id']),
    ForeignKeyConstraint(['pad_uuid'], ['pad.uuid'])
)


class Tag(db.Model):
    __tablename__ = 'tag'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    pads: Mapped[List['Pad']] = relationship('Pad', secondary=association_table, back_populates='tags')

    def __repr__(self):
        return f'<Tag text={self.text}>'

    @classmethod
    def get_or_create(cls, text):
        tag = cls.query.filter_by(text=text).first()
        if not tag:
            tag = cls(text=text)
            db.session.add(tag)
            db.session.commit()
        return tag
    
    # Return the list of most commonly used tags and their usage count
    @classmethod
    def get_most_common(cls, limit_n=None):
        query = (
            db.session.query(cls, func.count(association_table.c.pad_uuid).label('pad_count'))
            .join(association_table, cls.id == association_table.c.tag_id)
            .group_by(cls.id)
            .order_by(func.count(association_table.c.pad_uuid).desc())
        )

        if limit_n is not None:
            query = query.limit(limit_n)
        
        return query.all()
    
    # Return the list of most the n tags that are most commonly used with the given ones
    @classmethod
    def get_related_tags(cls, tag_list, n):
        res = (
            db.session.query(cls, func.count(association_table.c.pad_uuid).label('pad_count'))
            .join(association_table, cls.id == association_table.c.tag_id)
            .filter(association_table.c.pad_uuid.in_([p.uuid for p in tag_list[0].pads]))
            .filter(cls.text.notin_([t.text for t in tag_list]))
            .group_by(cls.id)
            .order_by(func.count(association_table.c.pad_uuid).desc())
            .limit(n)
        ).all()

        return [r[0] for r in res]
    


class Pad(db.Model):
    __tablename__ = 'pad'

    uuid: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    updatedAt: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)

    title: Mapped[str] = mapped_column(String)
    url: Mapped[str] = mapped_column(String, nullable=False)

    tags: Mapped[List['Tag']] = relationship('Tag', secondary=association_table, back_populates='pads')

    def __repr__(self):
        return f'<Pad uuid={self.uuid}, updatedAt={self.updatedAt}>'
    
    def sorted_tags(self):
        return sorted(self.tags, key=lambda t: t.text)

    # Return the pads which have all the given tags (matched by text string)
    @classmethod
    def get_by_taglist(cls, tag_text_list):
        if not tag_text_list:
            return []
        tags = Tag.query.filter(Tag.text.in_(tag_text_list)).all()

        return (
            db.session.query(cls)
            .join(association_table, cls.uuid == association_table.c.pad_uuid)
            .filter(association_table.c.tag_id.in_([t.id for t in tags]))
            .group_by(cls.uuid)
            .having(func.count(association_table.c.tag_id) == len(tags))
        ).all()


def drop_all():
    association_table.delete()
    Tag.query.delete()
    Pad.query.delete()
