import uuid
import unittest
from sqlalchemy_mock.utils import set_choice_fields_to_record, set_primary_key_to_record, compare_record_with_filter
from tests import Table, StatusEnum


class UtilsTestCase(unittest.TestCase):
    def test_set_choice_fields_to_record(self):
        row = Table(name="Row")
        row.status = "enable"
        set_choice_fields_to_record(row)
        self.assertEqual(row.status, StatusEnum.enable)

    def test_set_primary_key_to_record(self):
        row = Table(name="Row")
        set_primary_key_to_record(row, "uuid", lambda: str(uuid.uuid4()))
        self.assertNotEqual(row.uuid, None)

    def test_compare_record_with_filter(self):
        row = Table(name="Row")
        result = compare_record_with_filter(row, Table.name == "row")
        self.assertEqual(result, False)

        result = compare_record_with_filter(row, Table.name == "Row")
        self.assertNotEqual(result, False)

