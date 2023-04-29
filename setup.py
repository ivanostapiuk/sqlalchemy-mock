from setuptools import setup


setup(
    name='sqlalchemy-mock',
    version='0.1.0',
    description='The package for working with SQLAlchemy in unit tests',
    url='https://github.com/ivanostapiuk/sqlalchemy-mock',
    author='Ivan Ostapiuk',
    author_email='ost.ivan13@gmail.com',
    license='MIT',
    packages=['sqlalchemy_mock'],
    install_requires=['sqlalchemy']
)