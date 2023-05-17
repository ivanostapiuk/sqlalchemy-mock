import unittest.mock
import sqlalchemy


def set_choice_fields_to_record(record: object):
    for column in record.__table__.columns:
        if getattr(column.type, "choices", None):
            if isinstance(getattr(record, column.name), str):
                setattr(record, column.name, getattr(column.type.choices, getattr(record, column.name)))


def set_primary_key_to_record(record: object, primary_key: str, primary_key_generate: object):
    if not getattr(record, primary_key, None):
        setattr(record, primary_key, primary_key_generate())


def mock_sessions_methods(session: object):
    db_mock_methods = {method: unittest.mock.MagicMock(side_effect=getattr(session, method)) for method in ("query", "add", "add_all", "commit", "refresh")}
    return unittest.mock.patch.multiple(sqlalchemy.orm.Session, **db_mock_methods)


def compare_record_with_filter(record: object, filter: object):
    def _base_filter_handler(record: object, filter: object):
        field = getattr(record, filter.left.name)
        if not isinstance(field, str) and not field is None:
            field = field.value

        if not filter.operator(field, filter.right.value):
            return False

    def _in_op_filter_handler(record: object, filter: object):
        if not getattr(record, filter.left.name) in filter.right.value:
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

    filter_handlers = {
        "in_op": _in_op_filter_handler,
        "or_": _or_filter_handler
    }

    filter_operator =  filter.operator.__name__
    return filter_handlers.get(filter_operator, _base_filter_handler)(record, filter)
