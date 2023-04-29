from .utils import set_choice_fields_to_record, compare_record_with_filter


class Query:
    def __init__(self, session: object, instance: object, records: list):
        self.session = session
        self.instance = instance
        self.records = records
        self.limit_value = self.offset_value = None

    def __iter__(self):
        for record in self.records: yield record

    def __check_record_with_filter(self, record: object, filters: list):
        for filter in filters:
            result = compare_record_with_filter(record, filter)
            if result is not None: return result
        return True

    def filter(self, *filters: tuple):
        result = []
        for record in self.records:
            if self.__check_record_with_filter(record, list(filters)):
                result.append(record)

        self.records = result
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

    def order_by(self, value: object):
        if not value is None:
            if not getattr(value, "element", None) is None:
                if value.modifier.__name__ == "desc_op":
                    self.records.sort(key=lambda x: getattr(x, value.element.name), reverse=True)
            else:
                self.records.sort(key=lambda x: getattr(x, value.name))

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