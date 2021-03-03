import random
import app
from models import db, Actor, Movie

movies = Movie.query.all()

for movie in movies:
    """Randomly assign actors to movie."""
    actor_ids = random.sample(range(1, 11), 3)
    actors = Actor.query.filter(Actor.id.in_(actor_ids)).all()
    movie.actors = [actor for actor in actors]
    db.session.commit()
