# sqlalchemy-mock

The package for working with SQLAlchemy in unit tests,
it mocks requests to database, and provides necessary functionality within unit tests

It doesn't work with existing databases and doesn't create any tests databases, thanks to this it works enouth fast

## Installing
Exists a few aproaches to install package:

- You can clone this repository and run the next command to install package from local sourse:
    ```
    pip install -e /path/to/repository
    ```
- You can install this package from github:
    ```
    pip install git+https://github.com/ivanostapiuk/sqlalchemy-mock.git
    ```
- There is a package also in pypi:
    ```
    pip install sqlalchemy-mock
    ```

## How to use
By default primary key is 'uuid', but you can set another field as primary key and function to generate value, for example:

```python
import uuid


db = Session(primary_key="uuid", primary_key_generate=lambda: str(uuid.uuid4()))
```
A simple example how to use it in flask:

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
To run unittests use command:

```
python -m unittest
```