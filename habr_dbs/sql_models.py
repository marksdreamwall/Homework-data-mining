from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    String,
    create_engine)
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, unique=False, nullable=False)
    url = Column(String, unique=True, nullable=False)
    date_time = Column(String, unique=False)
    # writer_id = Column(Integer, ForeignKey('writer.id'))
    # comment_author = relationship('Post', back_populates='comment_author')

    def __init__(self, title, url, date_time):
        self.title = title
        self.url = url
        self.date_time = date_time

class Writer(Base):
    __tablename__ = 'writer'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=False, nullable=False)
    url = Column(String, unique=True, nullable=False)
    # post_id = Column(Integer, ForeignKey('post.id'))
    # writer = relationship('Writer', back_populates='post')


    def __init__(self, name, url):
        self.name = name
        self.url = url


class Comment_author(Base):
    __tablename__ = 'comment_author'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=False, nullable=False)
    url = Column(String, unique=True, nullable=False)
    # post_id = Column(Integer, ForeignKey('post.id'))

    def __init__(self, name, url):
        self.name = name
        self.url = url


