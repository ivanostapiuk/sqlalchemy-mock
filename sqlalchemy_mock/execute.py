from uuid import UUID
import sqlalchemy
from .utils import filter_records, sort_records, set_choice_fields_to_record


class Execute:
    def __init__(self, session: object, instance: object, expresion: object, records: list, selected_columns: list, sql_columns: list):
        self.session = session
        self.instance = instance
        self.expresion = expresion
        self.records = records
        self.selected_columns = selected_columns
        self.sql_columns = sql_columns
        self.filters = ()
        self.offset = None
        self.limit = None

    def __iter__(self):
        for record in self.records: yield record

    def __len__(self):
        return len(self.records)

    def _select(self):
        if not self.expresion._offset_clause is None:
            self.offset = self.expresion._offset_clause.value
        if not self.expresion._limit_clause is None:
            self.limit = self.expresion._limit_clause.value

        self.records = filter_records(self.filters, self.records)

        order_by = None
        if self.expresion._order_by_clauses:
            order_by = self.expresion._order_by_clauses[0]

        self.records = sort_records(order_by, self.records)
        return self

    def _update(self):
        self.records = filter_records(self.filters, self.records)
        for record in self.records:
            for field in self.expresion._values.keys():
                setattr(record, field.name, self.expresion._values[field].value)
            set_choice_fields_to_record(record)

    def _delete(self):
        self.records = filter_records(self.filters, self.records)
        self.session.delete(self.instance, self.records)

    def slice_records(self):
        limit = self.offset + self.limit if self.offset else self.limit
        self.records = self.records[self.offset:limit]

    def get_selected_columns(self):
        if len(self.selected_columns) == 1:
            return [getattr(record, self.selected_columns[0]) for record in self.records]
        else:
            result = []
            for record in self.records:
                result.append({column: getattr(record, column) for column in self.selected_columns})

            return result

    def set_sql_columns(self):
        for record in self.records:
            self.session.process_sql_columns(record, self.sql_columns)

    def set_uuid_fields(self):
        for record in self.records:
            for column in record.__table__.columns:
                if isinstance(column.type, sqlalchemy.sql.sqltypes.UUID) and not isinstance(getattr(record, column.key), UUID):
                    setattr(record, column.key, UUID(getattr(record, column.key)))

    def scalars(self):
        self.slice_records()
        self.set_uuid_fields()
        if self.sql_columns: self.set_sql_columns()
        if self.selected_columns: return self.get_selected_columns()
        return self

    def scalar_one(self):
        self.slice_records()
        self.set_uuid_fields()
        if self.sql_columns: self.set_sql_columns()
        if self.selected_columns:
            if self.selected_columns[0] == "count": return len(self.records)
            columns = self.get_selected_columns()
            if columns: return columns[0]
        return None

    def first(self):
        self.slice_records()
        if self.records:
            return self.records[0]
        return

    def process_filters(self):
        filters = []
        for filter_ in self.filters:
            if isinstance(filter_, sqlalchemy.sql.elements.BooleanClauseList) or not getattr(filter_.right, "value", None) is None:
                filters.append(filter_)
            elif isinstance(filter_.right, sqlalchemy.sql.selectable.ScalarSelect):
                setattr(filter_.right, "value", self.session.execute(filter_.right).scalars())
                filters.append(filter_)
            elif isinstance(filter_.right, sqlalchemy.sql.elements.True_):
                setattr(filter_.right, "value", True)
                filters.append(filter_)
            elif isinstance(filter_.right, sqlalchemy.sql.elements.False_):
                setattr(filter_.right, "value", False)
                filters.append(filter_)

        self.filters = filters

    def process(self):
        operations = {
            sqlalchemy.sql.selectable.Select: self._select,
            sqlalchemy.sql.dml.Update: self._update,
            sqlalchemy.sql.dml.Delete: self._delete
        }

        self.filters = self.expresion._where_criteria
        self.process_filters()

        return operations[type(self.expresion)]()