import unittest
from sqlalchemy import desc
from sqlalchemy_mock import Session
from tests import Table, StatusEnum


class QueryTestCase(unittest.TestCase):
    classmethod
    def setUp(cls):
        cls.session = Session()

    def test_filter(self):
        row_first = Table(name="RowFirst")
        row_second = Table(name="RowSecond")
        self.session.add_all([row_first, row_second])

        result = self.session.query(Table).filter(Table.name == "RowFirst").all()
        self.assertEqual(result[0].name, "RowFirst")

    def test_get_all(self):
        row_first = Table(name="RowFirst")
        row_second = Table(name="RowSecond")
        self.session.add_all([row_first, row_second])

        result = self.session.query(Table).all()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].name, "RowFirst")
        self.assertEqual(result[1].name, "RowSecond")

    def test_get_first(self):
        row_first = Table(name="RowFirst")
        self.session.add(row_first)

        result = self.session.query(Table).first()
        self.assertEqual(result.name, "RowFirst")

    def test_count(self):
        row_first = Table(name="RowFirst")
        row_second = Table(name="RowSecond")
        self.session.add_all([row_first, row_second])

        result = self.session.query(Table).count()
        self.assertEqual(result, 2)

    def test_order_by(self):
        row_first = Table(name="RowFirst")
        row_second = Table(name="RowSecond")
        self.session.add_all([row_first, row_second])

        result = self.session.query(Table).order_by(Table.name).all()
        self.assertEqual(result[0].name, "RowFirst")

        result = self.session.query(Table).order_by(desc(Table.name)).all()
        self.assertEqual(result[0].name, "RowSecond")

    def test_update(self):
        row = Table(name="Row", status="enable")
        self.session.add(row)
        self.session.query(Table).filter(Table.name == "Row").update({"status": "disable"})

        result = self.session.query(Table).first()
        self.assertEqual(result.status, StatusEnum.disable)

    def test_delete(self):
        row = Table(name="Row", status="enable")
        self.session.add(row)
        self.session.query(Table).filter(Table.name == "Row").delete()

        result = self.session.query(Table).count()
        self.assertEqual(result, 0)
