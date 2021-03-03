# FSND Capstone - Stellar Casting API
This is the capstone project for Udacity's Full Stack Web Developer Nanodegree program. 

Stellar Casting is an API for the management of movies and actors at a hypothetical casting agency. It implements authorization and RBAC through Auth0 and lets users view, add, modify, delete movies/actors from the database, and assign actors to movies.

See it live at https://stellar-casting.herokuapp.com/

The project covers the following skills:

* Modeling data objects with SQLAlchemy
* Developing a Flask API
* Authentication and Role-Based Access Control (RBAC) with Auth0
* Authentication in Flask
* Unit testing
* Schema migrations with Flask-Migrate
* Deployment on Heroku

## Tech Stack
* Python 3
* PostgreSQL
* Flask
* SQLAlchemy

## Development Setup

1. Download the code locally:
```bash
git clone https://github.com/mahri-a/stellar-casting.git
cd stellar-casting
```

2. Initialize and activate a virtual environment:
```bash
python -m virtualenv env
source env/bin/activate
```

3. Install the dependencies:
```bash
pip install -r requirements.txt
```

4. Create a postgresql database and optionally populate it using the `stellar.psql` file:
```bash
createdb stellar
psql stellar < stellar.psql
```

5. Change the DB variables in the `setup.sh` file and then set environment variables:
```bash
source setup.sh
```

6. Run the app:
```bash
python app.py
```

7. Navigate to [http://localhost:8080](http://localhost:8080)


## Testing

1. To run the unit tests, you will need valid access tokens. Navigate to [http://localhost:8080/authorization/url](http://localhost:8080/authorization/url) and open the link in a private window.

2. Below are three dummy Auth0 accounts. Log in with each account and copy the access token in the url. 

```bash
email: casting_assistant@gmail.com
password: Password1
```
```bash
email: casting_director@gmail.com
password: Password2
```
```bash
email: executive_producer@gmail.com
password: Password3
```

3. Update the access tokens in `setup.sh`.  

4. Create a test database and populate it using `stellar.psql`:
```bash
dropdb stellar_test
createdb stellar_test
psql stellar_test < stellar.psql
```

5. Set environment variables: 
```bash
source setup.sh
```

6. Run the tests:
```bash
python test_app.py
```


## API Reference
This API is based on REST principles. Endpoints return JSON data about movies and actors at Stellar Casting.

- [Actors Endpoints](#actors-endpoints)
  * [GET `/actors`](#get---actors-)
  * [POST `/actors`](#post---actors-)
  * [PATCH `/actors/{actor_id}`](#patch---actors--actor-id--)
  * [DELETE `/actors/{actor_id}`](#delete---actors--actor-id--)
- [Movies Endpoints](#movies-endpoints)
  * [GET `/movies`](#get---movies-)
  * [GET `/movies/{movie_id}/actors`](#get---movies--movie-id--actors-)
  * [POST `/movies`](#post---movies-)
  * [POST `/movies/{movie_id}/actors`](#post---movies--movie-id--actors-)
  * [PATCH `/movies/{movie_id}`](#patch---movies--movie-id--)
  * [DELETE `/movies/{int:id}`](#delete---movies--int-id--)
- [Errors](#errors)

### Authentication
All endpoints for movies and actors require `Authorization: Bearer {Auth0 access token}` in the request header. See [Testing](#testing) for how to get test access tokens.  


### Roles and Permissions

Casting Assistant:  
* `get:actors`  
* `get:movies`

Casting Director:  
* All Casting Assistant permissions
* `patch:actors`
* `patch:movies`
* `post:actors`
* `delete:actors`

Executive Producer:  
* All Casting Director permissions
* `post:movies`
* `delete:movies`


### Actors Endpoints
Actor attributes:
* `id`
* `name`
* `age`
* `gender`

#### GET `/actors`
Returns all actors. Results are paginated in groups of 5. Include a request parameter to choose a page, starting from 1.  

Example  
```bash
$ curl \
-H "Authorization: Bearer $CASTING_ASSISTANT_JWT" \
https://stellar-casting.herokuapp.com/actors?page=1
```

Response
```bash
{
    "records": [
        {
            "age": 30,
            "gender": "male",
            "id": 1,
            "name": "Jin Kazama"
        },
        {
            "age": 35,
            "gender": "male",
            "id": 2,
            "name": "Marshall Law"
        },
        {
            "age": 33,
            "gender": "female",
            "id": 3,
            "name": "Nina Williams"
        },
        {
            "age": 42,
            "gender": "male",
            "id": 4,
            "name": "Eddy Gordo"
        },
        {
            "age": 50,
            "gender": "male",
            "id": 5,
            "name": "Lei Wulong"
        }
    ],
    "success": true,
    "total_records": 10
}
```

#### POST `/actors`
`name`, `age`, and `gender` are required. 

Example  
```bash
$ curl -X POST \
-H "Authorization: Bearer $EXECUTIVE_PRODUCER_JWT" \
-H "Content-Type: application/json" \
-d '{"name": "Forest Law", "age": 70, "gender": "male"}' \
https://stellar-casting.herokuapp.com/actors
```

Response
```bash
{
    "added": {
        "age": 70,
        "gender": "male",
        "id": 12,
        "name": "Forest Law"
    },
    "success": true,
    "total_records": 12
}
```

#### PATCH `/actors/{actor_id}`

Example
```bash
$ curl -X PATCH \
-H "Authorization: Bearer $EXECUTIVE_PRODUCER_JWT" \
-H "Content-Type: application/json" \
-d '{"age": 27}' \
https://stellar-casting.herokuapp.com/actors/10
```

Response
```bash
{
    "success": true,
    "updated": {
        "age": 27,
        "gender": "female",
        "id": 10,
        "name": "Kazumi Mishima"
    }
}
```

#### DELETE `/actors/{actor_id}`

Example
```bash
$ curl -X DELETE \
-H "Authorization: Bearer $EXECUTIVE_PRODUCER_JWT" \
https://stellar-casting.herokuapp.com/actors/7
```

Response
```bash
{
    "deleted": {
        "age": 60,
        "gender": "female",
        "id": 7,
        "name": "Jun Kazama"
    },
    "success": true,
    "total_records": 11
}
```

### Movies Endpoints
Movie attributes:
* `id`
* `title`
* `release_date`

#### GET `/movies`
Returns all movies. Results are paginated in groups of 5. Include a request parameter to choose a page, starting from 1.  

Example
```bash
$ curl \
-H "Authorization: Bearer $CASTING_ASSISTANT_JWT" \
https://stellar-casting.herokuapp.com/movies
```

Response
```bash
{
    "records": [
        {
            "id": 1,
            "release_date": "Tue, 01 Oct 1991 00:00:00 GMT",
            "title": "My Neighbor Botero"
        },
        {
            "id": 2,
            "release_date": "Thu, 01 Jul 2021 00:00:00 GMT",
            "title": "Rumble in Tejen"
        },
        {
            "id": 3,
            "release_date": "Thu, 31 Dec 2020 00:00:00 GMT",
            "title": "13 Angry Men"
        },
        {
            "id": 4,
            "release_date": "Fri, 05 May 1995 00:00:00 GMT",
            "title": "Seven Sentinels"
        },
        {
            "id": 5,
            "release_date": "Mon, 05 Feb 1996 00:00:00 GMT",
            "title": "The Grand Ashgabat Hotel"
        }
    ],
    "success": true,
    "total_records": 5
}
```

#### GET `/movies/{movie_id}/actors`
Returns actors assigned to a specific movie.

Example
```bash
$ curl \
-H "Authorization: Bearer $CASTING_DIRECTOR_JWT" \
https://stellar-casting.herokuapp.com/movies/1/actors
```

Response
```bash
{
    "actors": [
        {
            "age": 33,
            "gender": "female",
            "id": 3,
            "name": "Nina Williams"
        },
        {
            "age": 42,
            "gender": "male",
            "id": 4,
            "name": "Eddy Gordo"
        }
    ],
    "movie_title": "My Neighbor Botero",
    "success": true,
    "total_actors": 2
}
```

#### POST `/movies`
`title` and `release_date` are required.  

Example  
```bash
$ curl -X POST \
-H "Authorization: Bearer $EXECUTIVE_PRODUCER_JWT" \
-H "Content-Type: application/json" \
-d '{"title": "Crouching Cat Hidden Turtle", "release_date": "2020-01-01"}' \
https://stellar-casting.herokuapp.com/movies
```

Response
```bash
{
    "added": {
        "id": 6,
        "release_date": "Wed, 01 Jan 2020 00:00:00 GMT",
        "title": "Crouching Cat Hidden Turtle"
    },
    "success": true,
    "total_records": 6
}
```

#### POST `/movies/{movie_id}/actors`
Assign an actor to a movie.

Example  
```bash
$ curl -X POST \
-H "Authorization: Bearer $CASTING_DIRECTOR_JWT" \
-H "Content-Type: application/json" \
-d '{"id": 4}' \
https://stellar-casting.herokuapp.com/movies/2/actors
```

Response
```bash
{
    "assigned": {
        "age": 42,
        "gender": "male",
        "id": 4,
        "name": "Eddy Gordo"
    },
    "success": true,
    "to_movie": {
        "id": 2,
        "release_date": "Thu, 01 Jul 2021 00:00:00 GMT",
        "title": "Rumble in Tejen"
    }
}
```

#### PATCH `/movies/{movie_id}`

Example
```bash
$ curl -X PATCH \
-H "Authorization: Bearer $EXECUTIVE_PRODUCER_JWT" \
-H "Content-Type: application/json" \
-d '{"release_date": "1990-05-05"}' \
https://stellar-casting.herokuapp.com/movies/4
```
Response
```bash
{
    "success": true,
    "updated": {
        "id": 4,
        "release_date": "Sat, 05 May 1990 00:00:00 GMT",
        "title": "Seven Sentinels"
    }
}
```

#### DELETE `/movies/{int:id}`

Example
```bash
$ curl -X DELETE \
-H "Authorization: Bearer $EXECUTIVE_PRODUCER_JWT" \
https://stellar-casting.herokuapp.com/movies/1
```

Response
```bash
{
    "deleted": {
        "id": 1,
        "release_date": "Tue, 01 Oct 1991 00:00:00 GMT",
        "title": "My Neighbor Botero"
    },
    "success": true,
    "total_records": 5
}
```

### Errors
The API will return the following error types when requests fail:
* 400: Bad request
* 404: Resource not found
* 405: Method not allowed
* 422: Unprocessable
* 401: Unauthorized

Example of a regular error object
```bash
{
    "error": 404,
    "message": "Resource not found",
    "success": false
}
```

Example of an authentication error object
```bash
{
    "code": "invalid_payload",
    "description": "Requested permission not in payload.",
    "error": 401,
    "success": false
}
```











