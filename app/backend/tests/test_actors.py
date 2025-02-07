import os
import unittest
import json
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import select
from src.api import create_app, db
from src.database.config import SQLALCHEMY_DATABASE_TEST_URI
from src.database.models import Actor, Gender, Movie


load_dotenv()
PRODUCER_TOKEN = os.getenv("PRODUCER_TOKEN")
headers = {"Authorization": f"Bearer {PRODUCER_TOKEN}"}


class ActorsTestCase(unittest.TestCase):
    """This class represents the test case for Actor data Model used in Flask app"""

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

    def test_actors_get(self):
        """Test Actors: GET Method - it should the actors"""
        res = self.client.get("/actors", headers=headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["actors"])

    def test_actors_fail_put_not_allowed(self):
        """Test Movies: PUT Method - it should returns not allowed"""
        res = self.client.put("/actors", headers=headers)
        self.assertEqual(res.status_code, 405)

    def test_actors_post(self):
        """Test Actors: Post Method - it should add a new actor"""
        res = self.client.post(
            "/actors",
            json={
                "name": "Edward Norton",
                "age": 31,
                "gender": Gender.MALE.name,
                "movies": [],
            },
            headers=headers,
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["actor"])

    def test_movies_post_missing_name(self):
        """Test Actors: Post Method - This should return error 400"""
        res = self.client.post(
            "/actors",
            json={
                "age": 31,
                "gender": Gender.MALE.name,
                "movies": [],
            },
            headers=headers,
        )
        self.assertEqual(res.status_code, 400)

    def test_get_actor_details(self):
        """Test Actor Details: GET Method - it should the actor details"""
        res = self.client.get("/actor-details/1", headers=headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["actor"])

    def test_actor_details_fail_post_not_allowed(self):
        """Test Actor Details: Post Method - it should returns not allowed"""
        res = self.client.post("/actor-details/1", headers=headers)
        self.assertEqual(res.status_code, 405)

    def test_actors_patch(self):
        """Test Actors: Patch Method - This should update the actors for id=1"""
        res = self.client.patch(
            "/actors/1",
            json={
                "name": "Edward Norton",
                "age": 31,
                "gender": Gender.MALE.name,
                "movies": [],
            },
            headers=headers,
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["actor"])

    def test_actors_patch_fail_missing_age(self):
        """Test Actors: Patch Method - This should return error 400 due to missing age"""
        res = self.client.patch(
            "/actors/1",
            json={
                "name": "Edward Norton",
                "gender": Gender.MALE.name,
                "movies": [],
            },
            headers=headers,
        )
        self.assertEqual(res.status_code, 400)

    def test_actors_delete(self):
        """Test Actors: Delete Method - This should delete actor that has id=1"""
        res = self.client.delete("/actors/1", headers=headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], 1)
        self.assertTrue(data["actor"])

    def test_actors_delete_fail_id_not_found(self):
        """Test Actors: Delete Method - FAIL id not found"""
        res = self.client.delete("/actors/666", headers=headers)
        self.assertEqual(res.status_code, 404)

    def test_actors_movies_relation_ship(self):
        """Test Actors: Actors/Movies Relationship"""
        stmt_select_movie = select(Movie).where(Movie.title == "Fight Club")
        with self.app.app_context():
            selected_movie = db.session.scalars(stmt_select_movie).one_or_none()

        self.client.patch(
            "/actors/1",
            json={
                "name": "Edward Norton",
                "age": 31,
                "gender": Gender.MALE.name,
                "movies": [selected_movie.id],
            },
            headers=headers,
        )

        stmt_select_actor = select(Actor).where(Actor.id == 1)
        with self.app.app_context():
            selected_actor = db.session.scalars(stmt_select_actor).one_or_none()
            self.assertEqual(selected_actor.movies[0].title, "Fight Club")


if __name__ == "__main__":
    unittest.main()
