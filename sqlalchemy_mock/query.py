from .utils import filter_records, set_choice_fields_to_record, sort_records


class Query:
    def __init__(self, session: object, instance: object, records: list):
        self.session = session
        self.instance = instance
        self.records = records
        self.limit_value = self.offset_value = None

    def __iter__(self):
        for record in self.records: yield record

    def filter(self, *filters: tuple):
        self.records = filter_records(filters, self.records)
        return self

    def count(self): return len(self.records)

    def all(self):
        offset = self.limit_value * self.offset_value if self.limit_value and self.offset_value else None
        limit = self.limit_value

        return self.records[offset:limit]

    def limit(self, size: int):
        self.limit_value = size
        return self

    def offset(self, value: int):
        self.offset_value = value
        return self

    def order_by(self, field: object):
        self.records = sort_records(field, self.records)
        return self

    def first(self):
        if self.records:
            return self.records[0]
        return

    def update(self, data: dict):
        for record in self.records:
            for key in data.keys():
                setattr(record, key, data[key])
            set_choice_fields_to_record(record)

    def delete(self):
        self.session.delete(self.instance, self.records)