import os
from sqlalchemy import Column, String, Integer, Date, UniqueConstraint
from flask_sqlalchemy import SQLAlchemy


DB_PATH = 'postgresql+psycopg2://{}:{}@{}/{}'.format(
    'mahri', 'pass', '127.0.0.1:5432', 'stellar')

db = SQLAlchemy()


def setup_db(app, database_path=DB_PATH):
    """Binds a flask application and a SQLAlchemy service."""
    app.config['SQLALCHEMY_DATABASE_URI'] = database_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)
    db.create_all()


association_table = db.Table('association',
    db.Column('movie_id', db.Integer, db.ForeignKey('movies.id'), primary_key=True),
    db.Column('actor_id', db.Integer, db.ForeignKey('actors.id'), primary_key=True)
)


class Movie(db.Model):
    __tablename__ = 'movies'
    __table_args__ = (UniqueConstraint('title', 'release_date'),)

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    release_date = Column(Date, nullable=False)
    
    actors = db.relationship('Actor', secondary=association_table,
        backref=db.backref('movies', lazy=True))

    def __init__(self, title, release_date):
        self.title = title,
        self.release_date = release_date

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self, attrs):
        print('update')
        for k, v in attrs.items():
            setattr(self, k, v)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'title': self.title,
            'release_date': self.release_date
        }


class Actor(db.Model):
    __tablename__ = 'actors'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)

    def __init__(self, name, age, gender):
        self.name = name
        self.age = age
        self.gender = gender

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self, attrs):
        print('update')
        for k, v in attrs.items():
            setattr(self, k, v)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f'<Actor ID: {self.id}, name: {self.name}>'

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age, 
            'gender': self.gender
        }







    


