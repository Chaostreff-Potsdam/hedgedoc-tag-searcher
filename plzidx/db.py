from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, ForeignKeyConstraint
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


class Pad(db.Model):
    __tablename__ = 'pad'

    uuid: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    updatedAt: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)

    tags: Mapped[List['Tag']] = relationship('Tag', secondary=association_table, back_populates='pads')

    def __repr__(self):
        return f'<Pad uuid={self.uuid}, updatedAt={self.updatedAt}>'
