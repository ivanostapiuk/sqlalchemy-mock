import uuid
from .query import Query
from .utils import set_choice_fields_to_record, set_primary_key_to_record, mock_sessions_methods


class Session:
    def __init__(self, primary_key: str = "uuid", primary_key_generate: object = lambda: str(uuid.uuid4())):
        self.__storage = {}
        self.primary_key = primary_key
        self.primary_key_generate = primary_key_generate

    def add(self, record: object):
        set_primary_key_to_record(record, self.primary_key, self.primary_key_generate)
        set_choice_fields_to_record(record)

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

    def refresh(self, record: object): return record

    def mock_session(self):
        return mock_sessions_methods(self)
