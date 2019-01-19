import datetime
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.pool import SingletonThreadPool, QueuePool

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False , unique=True)
    picture = Column(String(250))
    # @property
    # def serialize(self):
        # # returns obhect data in easily serilizable format
        # return {
            # 'name': self.name,
            # 'id': self.id,
			# 'email': self.email
        # }


class Collection(Base):
    __tablename__ = 'collection'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    @property
    def serialize(self):
        # returns obhect data in easily serilizable format
        return {
            'name': self.name,
            'id': self.id
        }


class ArticleCollection(Base):
    __tablename__ = 'article_item'

    name = Column(String(350), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    date = Column(
        String(80),
        default=datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S"))
    text = Column(Text())
	
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    collection_id = Column(Integer, ForeignKey('collection.id'))
    collection = relationship(Collection)

    @property
    def serialize(self):
        # returns obhect data in easily serilizable format
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'text': self.text,
			'date': self.date
        }


class Comments(Base):
    __tablename__ = 'comments'

    title = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    text = Column(Text())
    date = Column(
        String(80),
        default=datetime.datetime.now().strftime("%Y-%M-%D %H:%M"))
    article_id = Column(Integer, ForeignKey('article_item.id'))
    article_item = relationship(ArticleCollection)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)


engine = create_engine(
    'sqlite:///collectionsarticlesusers.db?check_same_thread=false')


Base.metadata.create_all(engine)
