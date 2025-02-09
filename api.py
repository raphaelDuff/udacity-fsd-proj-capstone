from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, jsonify, abort, render_template
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from flask_cors import CORS
from flask_migrate import Migrate
from database.models import Actor, Movie, db, Gender
from auth.auth import requires_auth, AuthError
import os

# Enable debug mode.
DEBUG = True
QUESTIONS_PER_PAGE = 10


# def paginate_drinks(request, selection, page_limit_number=QUESTIONS_PER_PAGE):
#     page = request.args.get("page", 1, type=int)
#     start = (page - 1) * page_limit_number
#     end = start + page_limit_number
#     drinks = [drink.short() for drink in selection]
#     current_drinks = drinks[start:end]
#     return current_drinks


def create_app(test_config=None):
    app = Flask(__name__)
    load_dotenv()

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS"
        )
        return response

    # Initialize the app with the extension
    config_path = os.path.join(os.path.dirname(__file__), "database", "config.py")
    app.config.from_pyfile(config_path, silent=False)

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    with app.app_context():
        db.create_all()

    # ROUTES

    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/movies", methods=["GET"])
    @requires_auth("get:movies")
    def get_movies(token):
        stmt_select_all_movies = select(Movie).order_by(Movie.id)
        movies = db.session.scalars(stmt_select_all_movies).all()
        list_movies = [movie.short() for movie in movies]
        if len(movies) == 0:
            abort(404)
        return jsonify({"success": True, "movies": list_movies})

    @app.route("/movie-details/<int:id>", methods=["GET"])
    @requires_auth("get:movie-details")
    def get_movie_detail(token, id):
        stmt_movie_by_id = select(Movie).where(Movie.id == id)
        selected_movie = db.session.scalars(stmt_movie_by_id).one_or_none()
        if selected_movie is None:
            abort(404)
        return jsonify({"success": True, "movie": selected_movie.long()})

    @app.route("/movies", methods=["POST"])
    def post_movie():
        try:
            data_json = request.get_json()
            if not data_json:
                abort(400)

            data_json_movie_title = data_json.get("title", None)
            data_json_release_date = data_json.get("release_date", None)
            data_json_actors = data_json.get("actors", None)

            if (
                data_json_movie_title is None
                or data_json_release_date is None
                or data_json_actors is None
            ):
                abort(400)

            release_date_datetime = datetime.strptime(
                str(data_json_release_date), "%d-%m-%Y"
            )

            actors = []

            if len(data_json_actors) > 0:
                stmt_select_actors_by_ids = select(Actor).where(
                    Actor.id.in_(data_json_actors)
                )
                actors = db.session.scalars(stmt_select_actors_by_ids).all()

            new_movie = Movie(
                title=data_json_movie_title,
                release_date=release_date_datetime,
                actors=actors,
            )
            db.session.add(new_movie)
            db.session.commit()

            return (
                jsonify({"success": True, "movie": new_movie.long()}),
                200,
            )
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500)
        finally:
            db.session.close()

    @app.route("/movies/<int:id>", methods=["PATCH"])
    @requires_auth("patch:movie")
    def update_movie(token, id):
        try:
            stmt_movie_by_id = select(Movie).where(Movie.id == id)
            selected_movie = db.session.scalars(stmt_movie_by_id).one_or_none()
            if selected_movie is None:
                abort(404)

            data_json = request.get_json()
            if not data_json:
                abort(400)

            data_json_movie_title = data_json.get("title", None)
            data_json_release_date = data_json.get("release_date", None)
            data_json_actors = data_json.get("actors", None)

            if (
                data_json_movie_title is None
                or data_json_release_date is None
                or data_json_actors is None
            ):
                abort(400)

            selected_movie.release_date = datetime.strptime(
                str(data_json_release_date), "%d-%m-%Y"
            )

            selected_movie.actors = []

            if len(data_json_actors) > 0:
                stmt_select_actors_by_ids = select(Actor).where(
                    Actor.id.in_(data_json_actors)
                )
                selected_movie.actors = db.session.scalars(
                    stmt_select_actors_by_ids
                ).all()

            selected_movie.title = data_json_movie_title
            selected_movie.release_date = data_json_release_date
            db.session.add(selected_movie)
            db.session.commit()
            return (
                jsonify({"success": True, "movie": selected_movie.long()}),
                200,
            )
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500)
        finally:
            db.session.close()

    @app.route("/movies/<int:id>", methods=["DELETE"])
    @requires_auth("del:movies")
    def delete_movie(token, id):
        try:
            stmt_movie_by_id = select(Movie).where(Movie.id == id)
            selected_movie = db.session.scalars(stmt_movie_by_id).one_or_none()
            if selected_movie is None:
                abort(404)

            db.session.delete(selected_movie)
            db.session.commit()

            return (
                jsonify(
                    {"success": True, "deleted": id, "movie": selected_movie.short()}
                ),
                200,
            )
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500)
        finally:
            db.session.close()

    @app.route("/actors", methods=["GET"])
    @requires_auth("get:actors")
    def get_actors(token):
        stmt_select_all_actors = select(Actor).order_by(Actor.id)
        actors = db.session.scalars(stmt_select_all_actors).all()
        list_actors = [actor.long() for actor in actors]
        if len(actors) == 0:
            abort(404)
        return jsonify({"success": True, "actors": list_actors})

    @app.route("/actor-details/<int:id>", methods=["GET"])
    @requires_auth("get:actor-details")
    def get_actor_detail(token, id):
        stmt_actor_by_id = select(Actor).where(Actor.id == id)
        selected_actor = db.session.scalars(stmt_actor_by_id).one_or_none()
        if selected_actor is None:
            abort(404)
        return jsonify({"success": True, "actor": selected_actor.long()})

    @app.route("/actors", methods=["POST"])
    @requires_auth("post:actors")
    def post_actor(token):
        try:

            data_json = request.get_json()
            if not data_json:
                abort(400)

            data_json_name = data_json.get("name", None)
            data_json_age = data_json.get("age", None)
            data_json_gender = data_json.get("gender", None)
            data_json_movies = data_json.get("movies", None)

            if (
                data_json_name is None
                or data_json_age is None
                or data_json_gender is None
                or data_json_movies is None
            ):
                abort(400)

            movies = []

            if len(data_json_movies) >= 0:
                stmt_select_movies_by_ids = select(Movie).where(
                    Movie.id.in_(data_json_movies)
                )
                movies = db.session.scalars(stmt_select_movies_by_ids).all()

            new_actor = Actor(
                name=data_json_name,
                age=data_json_age,
                gender=Gender(data_json_gender.capitalize()),
                movies=movies,
            )

            db.session.add(new_actor)
            db.session.commit()
            return (
                jsonify({"success": True, "actor": new_actor.long()}),
                200,
            )
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500)
        finally:
            db.session.close()

    @app.route("/actors/<int:id>", methods=["PATCH"])
    @requires_auth("patch:actor")
    def update_actor(token, id):
        try:
            stmt_actor_by_id = select(Actor).where(Actor.id == id)
            selected_actor = db.session.scalars(stmt_actor_by_id).one_or_none()
            if selected_actor is None:
                abort(404)

            data_json = request.get_json()
            if not data_json:
                abort(400)

            data_json_name = data_json.get("name", None)
            data_json_age = data_json.get("age", None)
            data_json_gender = data_json.get("gender", None)
            data_json_movies = data_json.get("movies", None)

            if (
                data_json_name is None
                or data_json_age is None
                or data_json_gender is None
                or data_json_movies is None
            ):
                abort(400)

            selected_actor.movies = []

            if len(data_json_movies) > 0:
                stmt_select_movies_by_ids = select(Movie).where(
                    Movie.id.in_(data_json_movies)
                )
                selected_actor.movies = db.session.scalars(
                    stmt_select_movies_by_ids
                ).all()

            selected_actor.name = data_json_name
            selected_actor.age = data_json_age
            selected_actor.gender = Gender(data_json_gender.capitalize())
            db.session.add(selected_actor)
            db.session.commit()
            return (
                jsonify({"success": True, "actor": selected_actor.long()}),
                200,
            )
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500)
        finally:
            db.session.close()

    @app.route("/actors/<int:id>", methods=["DELETE"])
    @requires_auth("del:actors")
    def delete_actor(token, id):
        try:
            stmt_actor_by_id = select(Actor).where(Actor.id == id)
            selected_actor = db.session.scalars(stmt_actor_by_id).one_or_none()
            if selected_actor is None:
                abort(404)

            db.session.delete(selected_actor)
            db.session.commit()

            return (
                jsonify(
                    {"success": True, "deleted": id, "actor": selected_actor.short()}
                ),
                200,
            )
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500)
        finally:
            db.session.close()

    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify({"success": False, "error": 400, "message": "bad request"}),
            400,
        )

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(405)
    def not_allowed(error):
        return (
            jsonify({"success": False, "error": 405, "message": "method not allowed"}),
            405,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(500)
    def internal_error(error):
        return (
            jsonify(
                {"success": False, "error": 500, "message": "internal server error"}
            ),
            500,
        )

    @app.errorhandler(AuthError)
    def handle_auth_error(e):
        response = jsonify(e.error)
        response.status_code = e.status_code
        return response

    return app


app = create_app()
CORS(app)
migrate = Migrate(app, db)

if __name__ == "__main__":
    port = int(
        os.environ.get("PORT", 5000)
    )  # Get port from environment or default to 5000
    app.run(host="0.0.0.0", port=port)
