from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    google_id = Column(Integer, nullable=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=True)
    picture_url = Column(String(250), nullable=True)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
            'google_id': self.google_id,
            'email': self.email,
            'picture_url': self.picture_url
        }


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String, nullable=True)

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'user': self.user_id
        }


class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String, nullable=True)

    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category_id,
            'user': self.user_id
        }


engine = create_engine('sqlite:///itemcatalog.db')

Base.metadata.create_all(engine)
