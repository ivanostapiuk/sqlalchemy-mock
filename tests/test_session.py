import unittest
from sqlalchemy_mock import Session
from tests import Table


class SessionTestCase(unittest.TestCase):
    classmethod
    def setUp(cls):
        cls.session = Session()

    def test_add_record_to_session(self):
        row = Table(name="Row")
        self.session.add(row)

        self.assertEqual(self.session.query(Table).count(), 1)

    def test_add_bulk_records_to_session(self):
        row_first = Table(name="RowFirst")
        row_second = Table(name="RowSecond")
        self.session.add_all([row_first, row_second])

        self.assertEqual(self.session.query(Table).count(), 2)

    def test_delete_record_from_session(self):
        row = Table(name="row")
        self.session.add(row)
        self.session.query(Table).filter(Table.name == "row").delete()

        self.assertEqual(self.session.query(Table).count(), 0)
