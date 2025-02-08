import os
import unittest
import json
from datetime import datetime
import unittest.mock
from dotenv import load_dotenv
from sqlalchemy import select
from api import create_app, db
from database.config import SQLALCHEMY_DATABASE_TEST_URI
from database.models import Actor, Gender, Movie


load_dotenv()
PRODUCER_TOKEN = os.getenv("PRODUCER_TOKEN")
DIRECTOR_TOKEN = os.getenv("DIRECTOR_TOKEN")
ASSISTANT_TOKEN = os.getenv("ASSISTANT_TOKEN")
headers_producer = {"Authorization": f"Bearer {PRODUCER_TOKEN}"}
headers_director = {"Authorization": f"Bearer {DIRECTOR_TOKEN}"}
headers_assistant = {"Authorization": f"Bearer {ASSISTANT_TOKEN}"}

# Roles:
# Casting Assistant
#   - Can view actors and movies
# Casting Director
#   - All permissions a Casting Assistant has and…
#   - Add or delete an actor from the database
#   - Modify actors or movies
# Executive Producer
#   - All permissions a Casting Director has and…
#   - Add or delete a movie from the database


class RolesTestCase(unittest.TestCase):
    """This class represents the test case for Movie data Model used in Flask app"""

    def setUp(self) -> None:
        """Define test variables and initialize app"""
        self.test_config = {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": SQLALCHEMY_DATABASE_TEST_URI,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        }
        self.app = create_app(test_config=self.test_config)
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            db.session.add_all(
                [
                    Movie(
                        title="Fight Club",
                        release_date=datetime.strptime(str("01-01-1999"), "%d-%m-%Y"),
                    ),
                    Movie(
                        title="Titanic",
                        release_date=datetime.strptime(str("01-01-1997"), "%d-%m-%Y"),
                        actors=[],
                    ),
                    Actor(name="Brad Pitt", age=37, gender=Gender.MALE),
                    Actor(name="Leonardo DiCaprio", age=26, gender=Gender.MALE),
                ]
            )

            db.session.commit()

    def tearDown(self) -> None:
        """Executed after each test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    # PRODUCER

    def test_producer_movies_post(self):
        """Test Movies: Post Method - Only Producer should be able to add a new movie"""
        res = self.client.post(
            "/movies",
            json={"title": "Pi", "release_date": "07-08-1998", "actors": []},
            headers=headers_producer,
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["movie"])

    def test_producer_movies_delete(self):
        """Test Movies: Delete Method - Only Producer should be able to delete movie that has id=1"""
        res = self.client.delete("/movies/1", headers=headers_producer)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], 1)
        self.assertTrue(data["movie"])

    # DIRECTOR

    def test_director_movies_delete(self):
        """Test Movies: Delete Method - Fail - Only Producer should be able to delete movie that has id=1"""
        res = self.client.delete("/movies/1", headers=headers_director)
        self.assertEqual(res.status_code, 403)

    def test_actors_patch(self):
        """Test Actors: Patch Method - This should be able to update the actors for id=1"""
        res = self.client.patch(
            "/actors/1",
            json={
                "name": "Edward Norton",
                "age": 31,
                "gender": Gender.MALE.name,
                "movies": [],
            },
            headers=headers_director,
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["actor"])

    # ASSISTANT

    def test_assistant_movies_get(self):
        """Test Movies: GET Method - it should be able to see the movies"""
        res = self.client.get("/movies", headers=headers_assistant)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["movies"])

    def test_assistant_actor(self):
        """Test Actors: Post Method - Only Producer and Director should be able to patch a actor"""
        res = self.client.patch(
            "/actors/1",
            json={
                "name": "Edward Norton",
                "age": 31,
                "gender": Gender.MALE.name,
                "movies": [],
            },
            headers=headers_assistant,
        )
        self.assertEqual(res.status_code, 403)


if __name__ == "__main__":
    unittest.main()
