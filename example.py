import typing

import strawberry
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, scoped_session, sessionmaker

from strawberry_sqlalchemy_mapper import strawberry_dataclass_from_model

############
# Database #
############
engine = create_engine("sqlite:///")
session = scoped_session(sessionmaker(autocommit=False,
                                      autoflush=False,
                                      bind=engine))
Base = declarative_base()


#####################
# SQLAlchemy Models #
#####################

class AuthorModel(Base):
    __tablename__ = "author"
    id = Column(Integer, primary_key=True, autoincrement=True)

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

    books = relationship("BookModel", backref="author")


class BookModel(Base):
    __tablename__ = "book"
    book_id = Column(Integer, primary_key=True, autoincrement=True)

    title = Column(String, nullable=False)
    release_year = Column(Integer, nullable=False)

    author_id = Column(Integer, ForeignKey("author.id"), nullable=False)


######################
# Strawberry-GraphQL #
######################

@strawberry.type
@strawberry_dataclass_from_model(AuthorModel)
class Author:
    books: typing.List["Book"]


@strawberry.type
@strawberry_dataclass_from_model(BookModel)
class Book:
    author: "Author"


@strawberry.type
class Query:
    @strawberry.field
    def get_author(self, id: strawberry.ID) -> Author:
        return session.query(AuthorModel).get(id)

    @strawberry.field
    def get_all_authors(self) -> typing.List[Author]:
        return session.query(AuthorModel).all()

    @strawberry.field
    def get_book(self, id: strawberry.ID) -> Book:
        return session.query(BookModel).get(id)

    @strawberry.field
    def get_all_books(self) -> typing.List[Book]:
        return session.query(BookModel).all()


# Create models
Base.metadata.create_all(bind=engine)

# Fill database with test data
sharespeare = AuthorModel(first_name="William", last_name="Sharespeare")
rowling = AuthorModel(first_name="Joanne", last_name="Rowling")

session.add(sharespeare)
session.add(rowling)
session.flush()  # Makes id available on the model instances

session.add(BookModel(title="Richard III",
                      release_year=1592,
                      author_id=sharespeare.id))
session.add(BookModel(title="Romeo and Juliet",
                      release_year=1595,
                      author_id=sharespeare.id))
session.add(BookModel(title="Hamlet",
                      release_year=1599,
                      author_id=sharespeare.id))

session.add(BookModel(title="Harry Potter and the Philosopher's Stone",
                      release_year=1997,
                      author_id=rowling.id))
session.add(BookModel(title="Harry Potter and the Chamber of Secrets",
                      release_year=1998,
                      author_id=rowling.id))
session.add(BookModel(title="Harry Potter and the Prisoner of Azkaban",
                      release_year=1999,
                      author_id=rowling.id))

session.commit()

# strawberry graphql schema
# start server with strawberry server app
schema = strawberry.Schema(query=Query)
