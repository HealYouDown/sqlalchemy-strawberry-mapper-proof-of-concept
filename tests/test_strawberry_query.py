import datetime
import decimal
import sys
import unittest

import strawberry
from strawberry_sqlalchemy_mapper.dataclass_from_model import \
    strawberry_dataclass_from_model

from tests.database import Base, TestModel, engine, session


# Strawberry Type which gets all scalar types set based
# on the model
@strawberry.type
@strawberry_dataclass_from_model(TestModel)
class TestType:
    pass


@strawberry.type
class Query:
    @strawberry.field
    def get_test_model(self, id: strawberry.ID) -> TestType:
        return session.query(TestModel).get(id)


class TestStrawberryQuery(unittest.TestCase):
    def setUp(self) -> None:
        Base.metadata.create_all(bind=engine)

        # Insert a test row
        session.add(TestModel(
            big_integer=2**31 - 1,
            boolean=True,
            date=datetime.date(2021, 7, 16),
            date_time=datetime.datetime(2021, 3, 10, 10, 23, 15, 30),
            float_=3.14,
            integer=42,
            numeric=decimal.Decimal(15.13),
            small_integer=16,
            string="Strawberry rocks",
            text="I actually don't like strawberries, but shhh",
            time=datetime.time(12, 14, 16),
            unicode="🍓❤️",
            unicode_text="Strawberry rocks 🍓"
        ))
        session.commit()

        self.schema = strawberry.Schema(query=Query)

    def test_query(self):
        d = self.schema.execute_sync("""
            query {
                getTestModel(id: 1) {
                    boolean
                    date
                    time
                    dateTime
                    float_
                    smallInteger
                    bigInteger
                    integer
                    numeric
                    string
                    text
                    unicode
                    unicodeText
                }
            }
        """)
        self.assertIsNone(d.errors)
        self.assertDictEqual(d.data, {
            "getTestModel": {
                "boolean": True,
                "date": "2021-07-16",
                "time": "12:14:16",
                "dateTime": "2021-03-10T10:23:15.000030",
                "float_": 3.14,
                "smallInteger": 16,
                "bigInteger": 2147483647,
                "integer": 42,
                "numeric": "15.1300000000",  # decimal.Decimal is converted to str??
                "string": "Strawberry rocks",
                "text": "I actually don't like strawberries, but shhh",
                "unicode": "🍓❤️",
                "unicodeText": "Strawberry rocks 🍓"
            }
        })
