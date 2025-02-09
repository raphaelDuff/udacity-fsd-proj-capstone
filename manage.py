import os
from flask_script import Manager
from flask_migrate import Migrate
from api import create_app
from database.models import db

app = create_app()
migrate = Migrate(app, db)
manager = Manager(app)

if __name__ == "__main__":
    manager.run()
