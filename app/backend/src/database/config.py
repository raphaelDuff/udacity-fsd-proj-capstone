from dotenv import load_dotenv
import os


SECRET_KEY = os.urandom(32)
basedir = os.path.abspath(os.path.dirname(__file__))
DEBUG = True
load_dotenv()
db_user = os.getenv("POSTGRESQL_USER")
db_password = os.getenv("POSTGRESQL_PW")
db_url = os.getenv("DATABASE_URL")
database_name = "casting"
database_test_name = "casting_test"
SQLALCHEMY_DATABASE_URI = db_url

SQLALCHEMY_DATABASE_TEST_URI = (
    f"postgresql://{db_user}:{db_password}@localhost:5432/{database_test_name}"
)
