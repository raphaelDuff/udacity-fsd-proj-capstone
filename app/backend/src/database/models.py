from enum import Enum as PyEnum
from sqlalchemy import Date, Enum
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from flask_sqlalchemy import SQLAlchemy
import json


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class Movie(db.Model):
    __tablename__ = "movie"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    title: Mapped[str] = mapped_column(nullable=False)
    release_date: Mapped[str] = mapped_column(Date, nullable=False)

    def __init__(self, title, release_date):
        self.title = title
        self.release_date = release_date

    def short(self):
        return {"id": self.id, "title": self.title, "release_date": self.release_date}

    def __repr__(self):
        return json.dumps(self.short())


class Gender(PyEnum):
    MALE = "Male"
    FEMALE = "Female"


class Actor(db.Model):
    __tablename__ = "actor"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    age: Mapped[int] = mapped_column(nullable=False)
    gender: Gender = mapped_column(Enum(Gender), nullable=False)

    def __init__(self, id, name, age, gender):
        self.id = id
        self.name = name
        self.age = age
        self.gender = gender

    def short(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
        }

    def __repr__(self):
        return json.dumps(self.short())
