from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item

# Connect to Database and create database session
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

test_user = User(name='Test')

session.add(test_user)

games = Category(name='Games', user=test_user)
sports = Category(name='Sports', user=test_user)

session.add_all([games, sports])

chess = Item(name='Chess', category=games, user=test_user)
settlers_of_catan = Item(name='Settlers of Catan',
                         category=games, user=test_user)

basketball = Item(name='Basketball', category=sports, user=test_user)
soccer_ball = Item(name='Soccer Ball', category=sports, user=test_user)

session.add_all([chess, settlers_of_catan, basketball, soccer_ball])

session.commit()
