# Udacity Full Stack Developer Nanodegree - Capstone Project: Casting Management API

This project is the capstone project for the Udacity Full Stack Developer Nanodegree. It's a RESTful API built with Flask (Python) that manages movies and actors, including their relationships.  It incorporates authentication and role-based access control (RBAC) to secure the API endpoints.

Other projects from this course:
* **Flask and SQLAlchemy:** https://github.com/raphaelDuff/udacity-fsd-proj-01-sqlalchemy
* **API Development and Unit Tests**: https://github.com/raphaelDuff/udacity-fsd-proj-02-api-development 
* **Identity and Access Management:** https://github.com/raphaelDuff/udacity-fsd-proj-03-identity-and-access-management
* **Server Deployment:** https://github.com/raphaelDuff/udacity-fsd-proj-04-server-deployment


## Motivation

The motivation behind this project was to demonstrate the skills and knowledge acquired throughout the Udacity Full Stack Developer Nanodegree program.  It serves as a practical application of building a complete backend API with best practices, including database interaction, API design, security, and deployment.     

## Hosted API URL

The hosted API is currently deployed on [Render](https://render.com) and can be accessed at: [https://fsnd-capstone-api.onrender.com/](https://fsnd-capstone-api.onrender.com/)  _(Please note that this URL might change. Check the repository for the latest deployed URL.)_

## Project Dependencies

*   Python 3.12
*   Flask
*   Flask-SQLAlchemy
*   psycopg2 (PostgreSQL database driver)
*   python-dotenv
*   Flask-CORS
*   PyJWT
*   requests
*   gunicorn (for production serving)

## Local Development Instructions


1.  **Create a Virtual Environment (Recommended):**

    ```bash
    python3 -m venv venv  # Create the virtual environment
    source venv/bin/activate  # Activate the virtual environment (Linux/macOS)
    venv\Scripts\activate  # Activate the virtual environment (Windows)
    ```

2.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up Database:**

    *   Ensure you have PostgreSQL installed.
    *   Create a database named `casting` (or whatever you prefer) and a user with appropriate permissions.
    * Create another database to use with the unit tests. It could be `casting_test`
    *   Create a `.env` file in the root directory and add your database connection details:

    ```
    DATABASE_URL=postgresql://user:password@localhost:5432/movies_db
    ```

4.  **Run the Development Server:**

    ```bash
    FLASK_APP=api.py FLASK_DEBUG=True flask run
    ```

5.  **Or run using Docker:**

    ```bash
     docker build --tag fsdcasting . # Build Docker image
     docker run -p 8080:8080 -e DATABASE_URL=postgresql://{{user}}:{{password}}@host.docker.internal:5432/casting fsdcasting
    ```

## Run locally using Docker

This project is designed to be easily containerized with Docker for deployment.

1.  **Build the Docker Image:**

  ```bash
     docker build --tag fsdcasting . 
  ```

2.  **Run the Docker Container:**

  ```bash
    docker run -p 8080:8080 -e DATABASE_URL=postgresql://user:password@host.docker.internal:5432/database_name fsdcasting
  ```  
    
  *   Replace `user`, `password`, and `database_name` with your PostgreSQL credentials.
  *   `host.docker.internal` is used to connect to your host's postgresql running in your machine if you are running in docker desktop. If you are running your postgresql in a docker container, you must use the container name or ip address in this enviroment variable.

3.  **Deployment to Render:**

    *   Create a Render account.
    *   Connect your GitHub repository.
    *   Render will automatically build and deploy your application.
    *   Set the `DATABASE_URL` environment variable in the Render dashboard.

## Authentication and RBAC

This API uses JWT (JSON Web Tokens) for authentication and RBAC for authorization.

1.  **Authentication (Auth0):**

    *   To access protected endpoints, you need a valid JWT.
    *   You can obtain a JWT by registering a user and logging in (the specific implementation of this might vary depending on your auth service).  **This project uses Auth0 for authentication.**

2.  **Role-Based Access Control:**

    The API defines the following permissions:

    *   `get:movies`: Allows retrieving movies.
    *   `get:movie-details`: Allows retrieving details of a specific movie.
    *   `post:movies`: Allows creating new movies.
    *   `patch:movie`: Allows updating the movie's details.
    *   `del:movies`: Allows deleting movies.
    *   `get:actors`: Allows retrieving actors.
    *   `get:actor-details`: Allows retrieving details of a specific actor.
    *   `post:actors`: Allows creating new actors.
    *   `patch:actor`: Allows updating the actor's details.
    *   `del:actors`: Allows deleting actors.

    ### Roles

    **Casting Assistant**
    - Can view actors and movies

    **Casting Director**
    - All permissions a Casting Assistant has and…
    - Add or delete an actor from the database
    - Modify actors or movies

    **Executive Producer**
    - All permissions a Casting Director has and…
    - Add or delete a movie from the database

## API Behavior

The API provides the following endpoints:

*   **Movies:**

    *   `GET /movies`
        - Fetches a list of movies
        - Request Arguments: JWT Token
        - Returns: 
            - `movies`: that contains an object of `id`, `release_date`and `title`
            - `success`: boolean

        ```json 
        {
            "movies": [
                {
                    "id": 1,
                    "release_date": "Tue, 01 Jan 1991 00:00:00 GMT",
                    "title": "Tomates Verdes Fritos"
                },
                {
                    "id": 2,
                    "release_date": "Sat, 01 Jan 2000 00:00:00 GMT",
                    "title": "Pi"
                },
                {
                    "id": 5,
                    "release_date": "Sun, 10 Feb 1991 00:00:00 GMT",
                    "title": "Matrix"
                }
            ],
            "success": true
        }
        ```

    *   `GET /movie-details/<movie-id>`
        - Fetches the details of the requested movie
        - Request Arguments: JWT Token, movie-id
        - Returns: 
            - `movie`: that contains an object of `id`, `release_date`, `title` and `actors` with the actors id list
            - `success`: boolean

        ```json 
        {
            "movie": {
                "actors": [
                    1,
                    3,
                    4,
                    5
                ],
                "id": 12,
                "release_date": "Tue, 10 Feb 2015 00:00:00 GMT",
                "title": "Lost in Translation"
            },
            "success": true
        }
        ```

        `POST '/movies'`
        - Sends a post request in order to add a new movie
        - Request Arguments: JWT Token
        - Request Body
        ```json
        {
            "title": "Ainda estou aqui",
            "release_date": "08-02-2025",
            "actors": []
        }
        ```
        - Returns: the `movie` object and the `success`boolean

        ```json 
        {
            "movie": {
                "actors": [],
                "id": 14,
                "release_date": "Sat, 08 Feb 2025 00:00:00 GMT",
                "title": "Ainda estou aqui"
            },
            "success": true
        }
        ```

        `PATCH '/movies/<movie-id>'`
        - Sends a post request in order to update the movie info
        - Request Arguments: JWT Token, movie-id
        - Request Body
        ```json
        {
            "title": "Ainda estou aqui",
            "release_date": "07-11-2024",
            "actors": []
        }
        ```
        - Returns: the `movie` object and the `success`boolean

        ```json 
        {
            "movie": {
                "actors": [],
                "id": 14,
                "release_date": "Sat, 07 Nov 2024 00:00:00 GMT",
                "title": "Ainda estou aqui"
            },
            "success": true
        }
        ```

    *   `DELETE /movies/<movie-id>`
        - Delete requested movie
        - Request Arguments: JWT Token, movie-id
        - Returns: 
            - `deleted`: movie id that was deleted
            - `movie`: that contains an object of `id`, `release_date`, `title` and `actors` with the actors id list
            - `success`: boolean

        ```json 
        {
            "deleted": 14,
            "movie": {
                "id": 14,
                "release_date": "Sat, 08 Feb 2025 00:00:00 GMT",
                "title": "Ainda estou aqui"
            },
            "success": true
        }
        ```


*   **Actors:**
    Follows the same logic and variables strategies used for Movie's endpoints
    *   `GET /actors`: Retrieves a list of actors.
    *   `GET /actor-details/<int:id>`: Retrieves details of a specific actor.
    *   `POST /actors`: Creates a new actor.
    *   `PATCH /actors/<int:id>`: Updates an actor.
    *   `DELETE /actors/<int:id>`: Deletes an actor.

All endpoints except require authentication and the appropriate permissions.  The API returns JSON responses and appropriate HTTP status codes.  Error handling is implemented to provide informative error messages.

### Error Handling
Errors are returned as JSON objects in the following format:
```
{
    "success": False, 
    "error": 400,
    "message": "bad request"
}
```
The API will return three error types when requests fail:
- 400: Bad Request
- 404: Resource Not Found
- 422: Not Processable
- 500: Internal server error


## Testing

To deploy and run the tests:

```bash
cd backend
python -m unittest discover -s tests
```

This command will execute the 3 tests files:
* `test_movies.py`
* `test_actors.py`
* `test_roles.py`