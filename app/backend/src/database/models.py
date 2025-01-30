from enum import Enum as PyEnum
from sqlalchemy import Column, Date, Enum, ForeignKey, Integer, Table
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from flask_sqlalchemy import SQLAlchemy
import json


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


actor_movie_association = Table(
    "actors_movies",
    Base.metadata,
    Column("actor_id", Integer, ForeignKey("actors.id"), primary_key=True),
    Column("movie_id", Integer, ForeignKey("movies.id"), primary_key=True),
)


class Movie(db.Model):
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    title: Mapped[str] = mapped_column(nullable=False)
    release_date: Mapped[str] = mapped_column(Date, nullable=False)
    actors: Mapped[list["Actor"]] = relationship(
        "Actor", secondary=actor_movie_association, back_populates="movies"
    )

    def short(self):
        return {"id": self.id, "title": self.title, "release_date": self.release_date}

    def __repr__(self):
        return json.dumps(self.short())


class Gender(PyEnum):
    MALE = "Male"
    FEMALE = "Female"


class Actor(db.Model):
    __tablename__ = "actors"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    age: Mapped[int] = mapped_column(nullable=False)
    gender: Mapped[Gender] = mapped_column(
        Enum(Gender, name="gender_enum"), nullable=False
    )
    movies: Mapped[list[Movie]] = relationship(
        "Movie", secondary=actor_movie_association, back_populates="actors"
    )

    def short(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender.value,
        }

    def __repr__(self):
        return json.dumps(self.short())
