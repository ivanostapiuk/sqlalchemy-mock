# sqlalchemy-mock

A package for working with SQLAlchemy in unit tests.
It mocks database interactions and provides the necessary functionality for unit testing without a real database.

It does not work with existing databases and does not create test databases, which makes it fast and lightweight

## Installing
There are several ways to install the package:

- **From a local source**. You can clone this repository and install the package from the local source:
    ```
    pip install -e /path/to/repository
    ```
- **From GitHub**. You can install the package directly from GitHub:
    ```
    pip install git+https://github.com/ivanostapiuk/sqlalchemy-mock.git
    ```
- **From PyPI**. The package is also available on PyPI:
    ```
    pip install sqlalchemy-mock
    ```

## How to use
By default, the primary key field is uuid. However, you can configure a different field as the primary key and provide a custom value generation function, for example:
```python
import uuid


db = Session(primary_key="uuid", primary_key_generate=lambda: str(uuid.uuid4()))
```
A simple example of how to use it with Flask:

```python
import unittest
from app import flask_app
from sqlalchemy_mock import Session
from models import Model


class TestCase(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.app = flask_app.test_client()
        cls.db = Session()

    def test(self):
        row = Model(field1="value1", field2="value2", field3="value3")
        self.db.add(row)
        self.db.commit()

        with self.db.mock_session():
            response = self.app.get(f"/get/model/object/{row.uuid}")
            self.assertEqual(response.json["field1"], row.field1)
```


## Runinng unittests
To run the unit tests, use the following command:

```
python -m unittest
```
