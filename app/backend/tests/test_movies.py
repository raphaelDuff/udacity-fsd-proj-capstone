import os
import unittest
import json
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import select
from src.api import create_app, db
from src.database.config import SQLALCHEMY_DATABASE_TEST_URI
from src.database.models import Actor, Gender, Movie


class MoviesTestCase(unittest.TestCase):
    """This class represents the test case for Trivia flask app"""

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

    def test_movies_get(self):
        """Test Movies: GET Method - it should the movies"""
        res = self.client.get("/movies")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["movies"])

    def test_movies_fail_put_not_allowed(self):
        """Test Movies: PUT Method - it should returns not allowed"""
        res = self.client.put("/movies")
        self.assertEqual(res.status_code, 405)

    def test_movies_post(self):
        """Test Movies: Post Method - it should add a new movie"""
        res = self.client.post(
            "/movies", json={"title": "Pi", "release_date": "07-08-1998", "actors": []}
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["movie"])

    def test_movies_post_missing_title(self):
        """Test Movies: Post Method - This should return error 400"""
        res = self.client.post(
            "/movies", json={"release_date": "07-08-1998", "actors": []}
        )
        self.assertEqual(res.status_code, 400)

    def test_get_movie_details(self):
        """Test Movie Details: GET Method - it should the movies"""
        res = self.client.get("/movie-details/1")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["movie"])

    def test_movie_details_fail_post_not_allowed(self):
        """Test Movie Details: Post Method - it should returns not allowed"""
        res = self.client.post("/movie-details/1")
        self.assertEqual(res.status_code, 405)

    def test_movies_patch(self):
        """Test Movies: Patch Method - This should update release_date"""
        res = self.client.patch(
            "/movies/1",
            json={"title": "Fight Club", "release_date": "29-10-1999", "actors": []},
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["movie"])

    def test_movies_patch_fail_missing_title(self):
        """Test Movies: Patch Method - This should return error 400 due to missing title"""
        res = self.client.patch(
            "/movies/1", json={"release_date": "29-10-1999", "actors": []}
        )
        self.assertEqual(res.status_code, 400)

    def test_movies_delete(self):
        """Test Movies: Delete Method - This should delete movie that has id=1"""
        res = self.client.delete("/movies/1")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], 1)
        self.assertTrue(data["movie"])

    def test_movies_delete_fail_id_not_found(self):
        """Test Movies: Delete Method - FAIL id not found"""
        res = self.client.delete("/movies/666")
        self.assertEqual(res.status_code, 404)


if __name__ == "__main__":
    unittest.main()
