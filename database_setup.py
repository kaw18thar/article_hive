
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.pool import SingletonThreadPool, QueuePool

Base = declarative_base()


class Collection(Base):
    __tablename__ = 'collection'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)


class ArticleCollection(Base):
    __tablename__ = 'article_item'

    name = Column(String(350), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    date = Column(DateTime, default=func.now())
    text = Column(UnicodeText())
    collection_id = Column(Integer, ForeignKey('collection.id'))
    collection = relationship(Collection)
    @property
    def serialize(self):
        #returns obhect data in easily serilizable format
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'text': self.text
        }

class Comments(Base):
    __tablename__ = 'comments'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    text = Column(UnicodeText())
    date = Column(DateTime, default=func.now())
    article_id = Column(Integer, ForeignKey('article_item.id'))
    collection = relationship(ArticleCollection)


engine = create_engine('sqlite:///collectionsarticles.db?check_same_thread=false')


Base.metadata.create_all(engine)