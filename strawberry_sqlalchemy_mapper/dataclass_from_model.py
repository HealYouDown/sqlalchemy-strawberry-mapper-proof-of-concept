import datetime
import decimal
import re
import typing

from sqlalchemy.orm.mapper import Mapper
from sqlalchemy.orm.relationships import RelationshipProperty
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import (BigInteger, Boolean, Date, DateTime,
                                     Float, Integer, LargeBinary, Numeric,
                                     SmallInteger, String, Text, Time, Unicode,
                                     UnicodeText)


def get_annotations_for_scalars(
    model
) -> typing.Dict[str, typing.Any]:
    scalar_annotations = {}

    # Go through all columns defined on the model and
    # get a type annotation for the defined column type
    # E.g. String -> str, Integer -> int, Boolean -> bool, ...
    # Type annotations will also support optional keyword based
    # on the nullable parameter of the column object.
    for name, column in model.__table__.columns.items():
        column: Column

        nullable: bool = column.nullable

        # Valid strawberry scalar types:
        # https://strawberry.rocks/docs/types/scalars
        # SQLAlchemy Column types:
        # https://docs.sqlalchemy.org/en/14/core/type_basics.html#generic-types

        type_ = None
        if isinstance(column.type, BigInteger):
            type_ = int
        elif isinstance(column.type, Boolean):
            type_ = bool
        elif isinstance(column.type, Date):
            type_ = datetime.date
        elif isinstance(column.type, DateTime):
            type_ = datetime.datetime
        # elif isinstance(column.type, Enum):
        #     type_ = enum.Enum
        elif isinstance(column.type, Float):
            type_ = float
        elif isinstance(column.type, Integer):
            type_ = int
        # elif isinstance(column.type, Interval):
        #     type_ = datetime.timedelta
        elif isinstance(column.type, LargeBinary):
            type_ = bytes
        elif isinstance(column.type, Numeric):
            type_ = decimal.Decimal
        # elif isinstance(column.type, PickleType):
        #     type_ = bytes
        elif isinstance(column.type, SmallInteger):
            type_ = int
        elif isinstance(column.type, String):
            type_ = str
        elif isinstance(column.type, Text):
            type_ = str
        elif isinstance(column.type, Time):
            type_ = datetime.time
        elif isinstance(column.type, Unicode):
            type_ = str
        elif isinstance(column.type, UnicodeText):
            type_ = str
        else:
            raise NotImplementedError(
                f"No scalar resolver for type {column.type}"
            )

        if nullable:
            scalar_annotations[name] = typing.Optional[type_]
        else:
            scalar_annotations[name] = type_

    return scalar_annotations


def get_annotations_for_relationships(
    model
) -> typing.Dict[str, typing.Any]:
    # TODO / FIXME:
    # As of right now, it is assumed that all models are named
    # xxxModel and all strawberry types are named xxx.
    # For example AuthorModel (SQLAlchemy Model) with Author as the
    # strawberry type.
    # This is obviously not really practical, but I have no idea
    # how this could be changed.
    relationship_annotations = {}

    # Go through all defined relationships on the model object.
    for name, relationship in model.__mapper__.relationships.items():
        relationship: RelationshipProperty

        # ONE-TO-MANY Relationships defined like
        # posts = sqlalchemy.orm.relationship("Posts")
        # have as argument a str, which is the class name of the
        # model.
        if isinstance(relationship.argument, str):
            rel_cls_name = relationship.argument

        # If it's a backref from the parent class, we only have
        # the mapper object from which we can get the class name.
        elif isinstance(relationship.argument, Mapper):
            rel_cls_name = relationship.argument.class_.__name__

        # Replaces 'Model' at the end to an empty string
        # BookModel -> Book
        # ModelModel -> Model
        type_name: str = re.sub(r"Model$", "", rel_cls_name)

        # Direction of the relationship, can be
        # ONETOMANY 1:n
        # ONETOONE 1:1
        # MANYTOMANY n:n TODO
        direction: str = relationship.direction.name

        # TODO: Figure out typing.Optional for 1:1 relations

        if direction == "ONETOMANY":
            relationship_annotations[name] = typing.List[typing.ForwardRef(type_name)]
        elif direction == "ONETOONE":
            relationship_annotations[name] = typing.ForwardRef(type_name)


def strawberry_dataclass_from_model(
    model,
):
    def wrapper(cls):
        cls.__annotations__.update({
            **get_annotations_for_scalars(model),
            # **get_annotations_for_relationships(model),
        })
        return cls

    return wrapper
