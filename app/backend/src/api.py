import os
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, jsonify, abort
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from flask_cors import CORS

from .database.models import *

# from .auth.auth import requires_auth, AuthError


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


def create_app(test_config=None, db=db):
    app = Flask(__name__)
    load_dotenv()
    CORS(app, resources={r"/*": {"origins": "*"}})

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
    app.config.from_object("src.database.config")
    print("app config: ", app.config)

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    with app.app_context():
        db.create_all()
        # drink_recipe = '[{"name": "water", "color": "blue", "parts": 1}]'
        # drink = Drink(title="water", recipe=drink_recipe)
        # drink2_recipe = '[{"name": "fanta", "color": "orange", "parts": 1}]'
        # drink2 = Drink(title="fanta", recipe=drink2_recipe)
        # drink3_recipe = '[{"name": "coca", "color": "black", "parts": 1}]'
        # drink3 = Drink(title="coca", recipe=drink3_recipe)
        # db.session.add(drink)
        # db.session.add(drink2)
        # db.session.add(drink3)
        # db.session.commit()

    # ROUTES
    # @app.route("/drinks", methods=["GET"])
    # def get_drinks():
    #     stmt_select_all_drinks = select(Drink).order_by(Drink.id)
    #     drinks = db.session.scalars(stmt_select_all_drinks).all()
    #     list_drinks = [drink.short() for drink in drinks]
    #     if len(drinks) == 0:
    #         abort(404)
    #     return jsonify({"success": True, "drinks": list_drinks})

    # @app.route("/drinks-detail", methods=["GET"])
    # # @requires_auth("get:drinks-detail")
    # def get_drinks_detail(token):
    #     stmt_select_all_drinks = select(Drink).order_by(Drink.id)
    #     drinks = db.session.scalars(stmt_select_all_drinks).all()
    #     list_drinks = [drink.long() for drink in drinks]
    #     if len(drinks) == 0:
    #         abort(404)
    #     return jsonify({"success": True, "drinks": list_drinks})

    @app.route("/movies", methods=["POST"])
    def post_movie():
        try:
            data_json = request.get_json()
            if not data_json:
                abort(400)

            data_json_movie_title = data_json.get("title", None)
            data_json_release_date = data_json.get("release_date", None)
            data_json_actors = data_json.get("actors", None)

            if data_json_movie_title is None or data_json_release_date is None:
                abort(400)

            release_date_datetime = datetime.strptime(
                str(data_json_release_date), "%d-%m-%Y"
            )

            if data_json_actors is None:
                new_movie = Movie(
                    title=data_json_movie_title, release_date=release_date_datetime
                )
            else:
                stmt_select_actors_by_ids = select(Actor).where(
                    Actor.id.in_(data_json_actors)
                )
                actors_by_id_list = db.session.scalars(stmt_select_actors_by_ids).all()
                new_movie = Movie(
                    title=data_json_movie_title,
                    release_date=release_date_datetime,
                    actors=actors_by_id_list,
                )

            db.session.add(new_movie)
            db.session.commit()
            return (
                jsonify({"success": True, "movie": new_movie.short()}),
                200,
            )
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500)
        finally:
            db.session.close()

    @app.route("/movies/<int:id>", methods=["PATCH"])
    def update_movie(id):
        try:
            stmt_movie_by_id = select(Movie).where(Movie.id == id)
            selected_movie = db.session.scalars(stmt_movie_by_id).one_or_none()
            if selected_movie is None:
                abort(404)

            data_json = request.get_json()
            if not data_json:
                abort(400)

            selected_movie.title = data_json.get("title", selected_movie.title)
            data_json_release_date = data_json.get(
                "release_date", selected_movie.release_date
            )

            selected_movie.release_date = datetime.strptime(
                str(data_json_release_date), "%d-%m-%Y"
            )

            # TODO - first retrieve the MOVIES LIST to check if there is any before update the value
            # selected_actor.movies = data_json.get("movies", selected_actor.movies)

            db.session.add(selected_movie)
            db.session.commit()
            return (
                jsonify({"success": True, "movie": selected_movie.short()}),
                200,
            )
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500)
        finally:
            db.session.close()

    @app.route("/movies/<int:id>", methods=["DELETE"])
    def delete_movie(id):
        try:
            stmt_movie_by_id = select(Movie).where(Movie.id == id)
            selected_movie = db.session.scalars(stmt_movie_by_id).one_or_none()
            if selected_movie is None:
                abort(404)

            db.session.delete(selected_movie)
            db.session.commit()

            return (
                jsonify(
                    {"success": True, "deleted": id, "movie": selected_movie.title}
                ),
                200,
            )
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500)
        finally:
            db.session.close()

    @app.route("/actors", methods=["POST"])
    def post_actor():
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
            ):
                abort(400)

            if data_json_movies is None:
                new_actor = Actor(
                    name=data_json_name,
                    age=data_json_age,
                    gender=Gender(data_json_gender.capitalize()),
                )
            else:
                stmt_select_movies_by_ids = select(Movie).where(
                    Movie.id.in_(data_json_movies)
                )
                movies_by_ids = db.session.scalars(stmt_select_movies_by_ids).all()
                new_actor = Actor(
                    name=data_json_name,
                    age=data_json_age,
                    gender=Gender(data_json_gender.capitalize()),
                    movies=movies_by_ids,
                )

            db.session.add(new_actor)
            db.session.commit()
            return (
                jsonify({"success": True, "actor": new_actor.short()}),
                200,
            )
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500)
        finally:
            db.session.close()

    @app.route("/actors/<int:id>", methods=["PATCH"])
    def update_actor(id):
        try:
            stmt_actor_by_id = select(Actor).where(Actor.id == id)
            selected_actor = db.session.scalars(stmt_actor_by_id).one_or_none()
            if selected_actor is None:
                abort(404)

            data_json = request.get_json()
            if not data_json:
                abort(400)

            selected_actor.name = data_json.get("name", selected_actor.name)
            selected_actor.age = data_json.get("age", selected_actor.age)
            selected_actor.gender = data_json.get("gender", selected_actor.gender)
            # TODO - first retrieve the MOVIES LIST to check if there is any before update the value
            # selected_actor.movies = data_json.get("movies", selected_actor.movies)
            selected_actor.gender = Gender(selected_actor.gender.capitalize())

            db.session.add(selected_actor)
            db.session.commit()
            return (
                jsonify({"success": True, "actor": selected_actor.short()}),
                200,
            )
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500)
        finally:
            db.session.close()

    @app.route("/actors/<int:id>", methods=["DELETE"])
    def delete_actor(id):
        try:
            stmt_actor_by_id = select(Actor).where(Actor.id == id)
            selected_actor = db.session.scalars(stmt_actor_by_id).one_or_none()
            if selected_actor is None:
                abort(404)

            db.session.delete(selected_actor)
            db.session.commit()

            return (
                jsonify({"success": True, "deleted": id, "actor": selected_actor.name}),
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

    # @app.errorhandler(AuthError)
    # def handle_auth_error(e):
    #     response = jsonify(e.error)
    #     response.status_code = e.status_code
    #     return response

    return app


if __name__ == "__main__":
    create_app()
