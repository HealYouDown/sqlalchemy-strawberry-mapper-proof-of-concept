import datetime
import decimal
import unittest

from strawberry_sqlalchemy_mapper.dataclass_from_model import \
    get_annotations_for_scalars

from tests.database import TestModel


class TestModelInspection(unittest.TestCase):
    def test_scalar_annotations(self):
        annotations = get_annotations_for_scalars(TestModel)
        self.assertDictEqual(annotations, {
            "index": int,
            "boolean": bool,
            "date": datetime.date,
            "time": datetime.time,
            "date_time": datetime.datetime,
            "float_": float,
            "small_integer": int,
            "big_integer": int,
            "integer": int,
            "numeric": decimal.Decimal,
            "string": str,
            "text": str,
            "unicode": str,
            "unicode_text": str,
        })
