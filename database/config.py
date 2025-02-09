from dotenv import load_dotenv
import os

SECRET_KEY = os.urandom(32)
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()
db_user = os.getenv("POSTGRESQL_USER")
db_password = os.getenv("POSTGRESQL_PW")
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
if SQLALCHEMY_DATABASE_URI.startswith("postgres:"):
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace(
        "postgres:", "postgresql:", 1
    )

database_test_name = "casting_test"

SQLALCHEMY_DATABASE_TEST_URI = (
    f"postgresql://{db_user}:{db_password}@localhost:5432/{database_test_name}"
)
