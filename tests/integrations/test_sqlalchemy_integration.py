from datetime import date

from sqlalchemy import Column, String, Integer, Date
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from catchpoint import constants
from catchpoint.compat import PY2
from catchpoint.opentracing.tracer import CatchpointTracer

Base = declarative_base()


class Movie(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True)
    title = Column(String(250))
    release_date = Column(Date)

    def __init__(self, title, release_date):
        self.title = title
        self.release_date = release_date


def set_up_engine_and_table(url):
    # create an engine
    engine = create_engine(url)

    # create table
    Base.metadata.create_all(engine)

    tracer = CatchpointTracer.get_instance()
    tracer.clear()
    return engine


def test_sqlalchemy_session_pqsql():
    engine = set_up_engine_and_table('postgresql://user:userpass@localhost:5432/db')

    # create a configured "Session" class
    Session = sessionmaker(bind=engine)

    # create a Session
    session = Session()

    # create Movies
    pulp_fiction = Movie("Pulp Fiction", date(1995, 4, 14))

    session.add(pulp_fiction)
    session.commit()
    session.close()

    tracer = CatchpointTracer.get_instance()
    span = tracer.get_spans()[0]

    statement = "INSERT INTO movies (title, release_date) VALUES (%(title)s, %(release_date)s) RETURNING movies.id"

    assert span.domain_name == constants.DomainNames['DB']
    assert span.class_name == constants.ClassNames['POSTGRESQL']
    assert span.operation_name == 'db'
    assert span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'WRITE'
    assert span.get_tag(constants.SpanTags['DB_INSTANCE']) == 'db'
    assert span.get_tag(constants.SpanTags['DB_TYPE']) == "postgresql"
    assert span.get_tag(constants.SpanTags['DB_HOST']) == 'localhost'
    assert span.get_tag(constants.SpanTags['DB_STATEMENT']) == statement
    assert span.get_tag(constants.SpanTags['DB_STATEMENT_TYPE']) == 'INSERT'


def test_sqlalchemy_connection_execute_pqsql():
    engine = set_up_engine_and_table('postgresql://user:userpass@localhost:5432/db')

    query = "SELECT title FROM movies"
    connection = engine.connect()
    connection.execute(query)

    tracer = CatchpointTracer.get_instance()
    span = tracer.get_spans()[0]

    assert span.domain_name == constants.DomainNames['DB']
    assert span.class_name == constants.ClassNames['POSTGRESQL']
    assert span.operation_name == 'db'
    assert span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'READ'
    assert span.get_tag(constants.SpanTags['DB_INSTANCE']) == 'db'
    assert span.get_tag(constants.SpanTags['DB_HOST']) == 'localhost'
    assert span.get_tag(constants.SpanTags['DB_TYPE']) == "postgresql"
    assert span.get_tag(constants.SpanTags['DB_STATEMENT']) == query
    assert span.get_tag(constants.SpanTags['DB_STATEMENT_TYPE']) == 'SELECT'


def test_sqlalchemy_connection_execute_mysql():
    engine = set_up_engine_and_table('mysql+mysqlconnector://user:userpass@localhost:3306/db')

    query = "SELECT title FROM movies"
    connection = engine.connect()
    connection.execute(query)

    tracer = CatchpointTracer.get_instance()
    span = tracer.get_spans()[0]

    assert span.domain_name == constants.DomainNames['DB']
    assert span.class_name == constants.ClassNames['MYSQL']
    assert span.operation_name == 'db'
    assert span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'READ'
    assert span.get_tag(constants.SpanTags['DB_INSTANCE']) == 'db'
    assert span.get_tag(constants.SpanTags['DB_TYPE']) == "mysql"
    assert span.get_tag(constants.SpanTags['DB_HOST']) == 'localhost'
    assert span.get_tag(constants.SpanTags['DB_STATEMENT']) == query
    assert span.get_tag(constants.SpanTags['DB_STATEMENT_TYPE']) == 'SELECT'


def test_sqlalchemy_connection_execute_mysql_error():
    engine = set_up_engine_and_table('mysql+mysqlconnector://user:userpass@localhost:3306/db')

    query = "SELECT title FROM test"
    connection = engine.connect()
    try:
        connection.execute(query)
    except:
        pass
    tracer = CatchpointTracer.get_instance()
    span = tracer.get_spans()[0]

    assert span.domain_name == constants.DomainNames['DB']
    assert span.class_name == constants.ClassNames['MYSQL']
    assert span.operation_name == 'db'
    assert span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'READ'
    assert span.get_tag(constants.SpanTags['DB_INSTANCE']) == 'db'
    assert span.get_tag(constants.SpanTags['DB_TYPE']) == "mysql"
    assert span.get_tag(constants.SpanTags['DB_HOST']) == 'localhost'
    assert span.get_tag(constants.SpanTags['DB_STATEMENT']) == query
    assert span.get_tag(constants.SpanTags['DB_STATEMENT_TYPE']) == 'SELECT'
    assert span.get_tag("error") is True


def test_sqlalchemy_connection_execute_sqlite():
    if not PY2:
        engine = set_up_engine_and_table('sqlite:///:memory:')

        query = "SELECT title FROM movies"
        connection = engine.connect()
        connection.execute(query)

        tracer = CatchpointTracer.get_instance()
        span = tracer.get_spans()[0]

        assert span.domain_name == constants.DomainNames['DB']
        assert span.class_name == constants.ClassNames['SQLITE']
        assert span.operation_name == ':memory:'
        assert span.get_tag(constants.SpanTags['OPERATION_TYPE']) == 'READ'
        assert span.get_tag(constants.SpanTags['DB_INSTANCE']) == ':memory:'
        assert span.get_tag(constants.SpanTags['DB_TYPE']) == "sqlite"
        assert span.get_tag(constants.SpanTags['DB_HOST']) == ''
        assert span.get_tag(constants.SpanTags['DB_STATEMENT']) == query
        assert span.get_tag(constants.SpanTags['DB_STATEMENT_TYPE']) == 'SELECT'
