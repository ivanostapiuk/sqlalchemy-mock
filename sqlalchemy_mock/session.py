import uuid
import sqlalchemy

from .query import Query
from .execute import Execute
from .utils import set_choice_fields_to_record, set_primary_key_to_record, mock_sessions_methods, set_default_fields


class Session:
    def __init__(self, primary_key: str = "uuid", primary_key_generate: object = lambda: str(uuid.uuid4())):
        self.__storage = {}
        self.primary_key = primary_key
        self.primary_key_generate = primary_key_generate

    def add(self, record: object, *args, **kwargs):
        set_primary_key_to_record(record, self.primary_key, self.primary_key_generate)
        set_choice_fields_to_record(record)
        set_default_fields(record)

        record_table = str(type(record))
        if not record_table in self.__storage:
            self.__storage[record_table] = [record]
        else:
            self.__storage[record_table].append(record)

    def add_all(self, records: list):
        for record in records: self.add(record)

    def query(self, instance: object):
        records = self.__storage.get(str(instance), [])
        return Query(self, instance, records)

    def delete(self, instance: object, records: list):
        for record in records:
            self.__storage[str(instance)].remove(record)

    def commit(self): ...

    def flush(self): ...

    def get_label_columns(self, model: object):
        label_columns = []
        for column in sqlalchemy.inspection.inspect(model).c:
            if isinstance(column, sqlalchemy.sql.elements.Label):
                label_columns.append(column)

        return label_columns

    def process_sql_columns(self, record: object, label_columns: list):
        for column in label_columns:
            for filter_ in column.element._where_criteria:
                if isinstance(filter_.right, sqlalchemy.sql.annotation.AnnotatedColumn):
                    setattr(filter_.right, "value", getattr(record, filter_.right.key, None))

            setattr(record, column.key, self.execute(column.element).scalar_one())

    def refresh(self, record: object, *args, **kwargs):
        label_columns = self.get_label_columns(record.__class__)
        record = self.process_sql_columns(record, label_columns)
        return record

    def mock_session(self):
        return mock_sessions_methods(self)

    def bulk_insert_mappings(self, table, values):
        records = [table(**record) for record in values]
        self.add_all(records)

    def get_records_by_instance(self, instance: object):
        return self.__storage.get(str(instance), [])

    def execute(self, expresion: object, *args, **kwargs):
        if not getattr(expresion, "element", None) is None:
            expresion = expresion.element

        expresion_selected_columns = getattr(expresion, "selected_columns", [])
        instance = expresion._propagate_attrs["plugin_subject"].class_
        selected_columns = [column.name for column in expresion_selected_columns]
        records = self.__storage.get(str(instance), [])

        if not getattr(expresion, "_raw_columns", None) is None and not getattr(expresion._raw_columns[0], "_columns", None) is None:
            selected_columns = []

        sql_columns = []
        for selected_column in expresion_selected_columns:
            if not getattr(selected_column, "element", None) is None:
                sql_columns.append(selected_column)

        execute = Execute(self, instance, expresion, records, selected_columns, sql_columns)
        return execute.process()