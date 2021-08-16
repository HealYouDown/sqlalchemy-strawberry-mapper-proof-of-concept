# Strawberry Dataclass from SQLAlchemy-Model
Using a decorator, we can map the model columns automatically to a dataclass which is used as a `strawberry.type`.

## Features
- Automatically sets a type annotation for all supported types below
- Respects `nullable` on the column and will add `typing.Optional` if needed

Relationships are **NOT** supported automatically. You will have to add them yourself to the `strawberry.type` dataclasses.

> There is some code which tries to get the relationship from the mapper of the model, but this requires to know upfront how the models and dataclasses are mapped (e.g. BookModel -> Book). You could theoretically assume that all models end with ..Model, but I don't want to go that route.

## Would be nice to have as a feature
- Allow a list of columns to be passed which should be excluded from the mapping

## Supported types
|SQLAlchemy Column Type|Python Type|Mapping Supported|
|:--|:--:|:--:|
|`Integer`|`int`|✔️|
|`SmallInteger`|`int`|✔️|
|`BigInteger`|`int`|✔️|
|`Numeric`|`decimal.Decimal`|✔️|
|`Float`|`float`|✔️|
|`Boolean`|`bool`|✔️|
|`Enum`|`enum.Enum`|❌|
|`Date`|`datetime.date`|✔️|
|`Time`|`datetime.time`|✔️|
|`Interval`|`datetime.Interval`|❌|
|`DateTime`|`datetime.datetime`|✔️|
|`String`|`str`|✔️|
|`Text`|`str`|✔️|
|`Unicode`|`str`|✔️|
|`UnicodeText`|`str`|✔️|
|`PickleType`|`-`|❌|
|`LargeBinary`|`bytes`|❌|

## Example
To run the example, use `strawberry server example` which will start a local GraphiQL server on [localhost:8000/graphql](localhost:8000/graphql).

The example explained below can be found in `example.py`

### SQLAlchemy
#### Create a database
Using SQLAlchemy, we will create a sqlite3 database in memory.

```py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("sqlite:///")
session = scoped_session(sessionmaker(autocommit=False,
                                      autoflush=False,
                                      bind=engine))
Base = declarative_base()
```

#### Create the database models
We will go for a simple example with two models: An author and their books.

```py
from sqlalchemy import Column, String, Integer, ForeignKey,
from sqlalchemy.orm import relationship

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
```

### Create the strawberry 🍓
#### Types
Using the `@strawberry_dataclass_from_model(model)` decorator, we don't need to write all fields with their type hints again. The model will be inspected and annotations will be set accordingly.

```py
from strawberry_sqlalchemy_mapper import strawberry_dataclass_from_model
import strawberry
import typing

@strawberry.type
@strawberry_dataclass_from_model(AuthorModel)
class Author:
    books: typing.List["Book"]


@strawberry.type
@strawberry_dataclass_from_model(BookModel)
class Book:
    author: "Author"
```

#### Query
A simple strawberry query which allows us to query a single author or book by id or all authors and books.
```py
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
```

### Example queries
```gql
query {
  getAuthor(id: 1) {
    firstName
    lastName
    books {
      title
      releaseYear
    }
  }
  
  getAllAuthors {
    firstName
    lastName
    books {
      title
      releaseYear
    }
  }
  
  getBook(id: 1) {
    title
    releaseYear
    author {
      firstName
      lastName
    }
  }
  
  getAllBooks {
    title
    releaseYear
    author {
      firstName
      lastName
    }
  }
}
```