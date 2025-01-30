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
            # data = request.get_json()
            # drink_title = data.get("title", None)
            # drink_recipe = json.dumps(data.get("recipe", None))
            movie_title = "Tomates Verdes Fritos"
            release_date_str = "1991"
            release_date_datetime = datetime.strptime(release_date_str, "%Y")
            stmt_select_actor_by_id = select(Actor).where(Actor.id == 1)
            data_actor_by_id = db.session.scalars(stmt_select_actor_by_id).one()
            actors_by_id_list = [data_actor_by_id]

            if movie_title is None or release_date_str is None:
                abort(400)

            new_movie = Movie(
                title=movie_title,
                release_date=release_date_datetime,
                actors=actors_by_id_list,
            )
            db.session.add(new_movie)
            db.session.commit()
            # return redirect(
            #     url_for(
            #         "get_drinks",
            #         result=jsonify({"success": True, "drinks": new_drink.long()}),
            #     )
            # )
            return (
                jsonify({"success": True, "movie": new_movie.short()}),
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
            # data = request.get_json()
            # drink_title = data.get("title", None)
            # drink_recipe = json.dumps(data.get("recipe", None))
            actor_name = "Danilo Hank"
            actor_age = 36
            actor_gender = Gender.MALE

            if actor_name is None or actor_age is None or actor_gender is None:
                abort(400)

            new_actor = Actor(name=actor_name, age=actor_age, gender=actor_gender)
            db.session.add(new_actor)
            db.session.commit()
            # return redirect(
            #     url_for(
            #         "get_drinks",
            #         result=jsonify({"success": True, "drinks": new_drink.long()}),
            #     )
            # )
            return (
                jsonify({"success": True, "actor": new_actor.short()}),
                200,
            )
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500)
        finally:
            db.session.close()

    # @app.route("/drinks/<int:id>", methods=["PATCH"])
    # # @requires_auth("patch:drinks")
    # def update_drink(token, id):
    #     try:
    #         stmt_drink_by_id = select(Drink).where(Drink.id == id)
    #         selected_drink = db.session.scalars(stmt_drink_by_id).one_or_none()
    #         if selected_drink is None:
    #             abort(404)

    #         data = request.get_json()
    #         if not data:
    #             abort(400)
    #         selected_drink.title = data.get("title", selected_drink.title)
    #         selected_drink.recipe = json.dumps(
    #             data.get("recipe", selected_drink.recipe)
    #         )
    #         db.session.add(selected_drink)
    #         db.session.commit()
    #         return (
    #             jsonify({"success": True, "drinks": selected_drink.long()}),
    #             200,
    #         )
    #     except SQLAlchemyError as e:
    #         db.session.rollback()
    #         abort(500)
    #     finally:
    #         db.session.close()

    # @app.route("/drinks/<int:id>", methods=["DELETE"])
    # @requires_auth("delete:drinks")
    # def delete_drink(token, id):
    #     try:
    #         stmt_drink_by_id = select(Drink).where(Drink.id == id)
    #         selected_drink = db.session.scalars(stmt_drink_by_id).one_or_none()
    #         if selected_drink is None:
    #             abort(404)

    #         db.session.delete(selected_drink)
    #         db.session.commit()

    #         return (
    #             jsonify(
    #                 {
    #                     "success": True,
    #                     "deleted": id,
    #                 }
    #             ),
    #             200,
    #         )
    #     except SQLAlchemyError as e:
    #         db.session.rollback()
    #         abort(500)
    #     finally:
    #         db.session.close()

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
