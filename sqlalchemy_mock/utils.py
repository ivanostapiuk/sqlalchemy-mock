from uuid import UUID
import datetime
from types import FunctionType
import unittest.mock
import sqlalchemy


def set_choice_fields_to_record(record: object):
    for column in record.__table__.columns:
        enum_attribute = None
        if getattr(column.type, "enum_class", None): enum_attribute = "enum_class"
        if getattr(column.type, "choices", None): enum_attribute = "choices"

        if enum_attribute and isinstance(getattr(record, column.name), str):
            setattr(record, column.name, getattr(getattr(column.type, enum_attribute), getattr(record, column.name)))

def set_primary_key_to_record(record: object, primary_key: str, primary_key_generate: object):
    if not getattr(record, primary_key, None):
        setattr(record, primary_key, primary_key_generate())


def set_default_fields(record: object):
    functions = {
        "utcnow": datetime.datetime.utcnow
    }

    for column in record.__class__.__table__._columns:
        if column.default and not getattr(record, column.name, None):
            value = column.default.arg
            if isinstance(column.default.arg, FunctionType):
                value = functions.get(column.default.arg.__name__, value)()
            setattr(record, column.name, value)


def mock_sessions_methods(session: object):
    db_mock_methods = {method: unittest.mock.MagicMock(side_effect=getattr(session, method)) for method in ("query", "add", "add_all", "commit", "refresh", "execute", "bulk_insert_mappings")}
    return unittest.mock.patch.multiple(sqlalchemy.orm.Session, **db_mock_methods)


def compare_record_with_filter(record: object, filter: object):
    def _base_filter_handler(record: object, filter: object):
        field = getattr(record, filter.left.name)

        if isinstance(field, UUID) or isinstance(field, int):
            field = str(field)
        elif not isinstance(field, str) and not isinstance(field, bool) and not field is None:
            field = field.value

        value = filter.right.value
        if not isinstance(value, str) and not isinstance(value, bool) and not value is None:
            value = str(value)

        if not filter.operator(field, value):
            return False

    def _in_op_filter_handler(record: object, filter: object):
        values = []
        for value in filter.right.value:
            value = str(value) if isinstance(value, UUID) else value
            values.append(value)

        field = getattr(record, filter.left.name)
        field = str(field) if isinstance(field, UUID) else field

        if not field in values:
            return False

    def _or_filter_handler(record: object, filter: object):
        result = False
        for part in filter:
            if not getattr(part.left, "clause_expr", None) is None and part.left.clause_expr.element.operator.__name__ == "comma_op":
                record_field = getattr(record, part.left.clause_expr.element.clauses[0].name)
                if part.left.name in ("lower", "upper"):
                    record_field = getattr(record_field, part.left.name)()

                if part.right.value in record_field:
                    result = True

        return result

    def _contains_op_filter_handler(record: object, filter: object):
        record_field = getattr(record, filter.left.clause_expr.element.clauses[0].name)
        if filter.left.name in ("lower", "upper"):
            record_field = getattr(record_field, filter.left.name)()

        if not filter.right.value in record_field:
            return False

    filter_handlers = {
        "in_op": _in_op_filter_handler,
        "or_": _or_filter_handler,
        "contains_op": _contains_op_filter_handler
    }

    filter_operator =  filter.operator.__name__
    return filter_handlers.get(filter_operator, _base_filter_handler)(record, filter)


def check_record_with_filter(record: object, filters: list):
    for filter in filters:
        result = compare_record_with_filter(record, filter)
        if result is not None: return result
    return True


def filter_records(filters: tuple, records: list):
    result = []
    for record in records:
        if check_record_with_filter(record, list(filters)):
            result.append(record)

    return result


def sort_records(field: object, records: list):
    if not field is None:
        if not getattr(field, "element", None) is None:
            if field.modifier.__name__ == "desc_op":
                records.sort(key=lambda x: getattr(x, field.element.name), reverse=True)
        else:
            records.sort(key=lambda x: getattr(x, field.name))

    return records