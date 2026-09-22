from sqlalchemy import text

from app.db.base import Base
from app.db.session import create_database_engine


def test_database_engine_can_execute_a_query() -> None:
    engine = create_database_engine("sqlite+pysqlite:///:memory:")

    with engine.connect() as connection:
        assert connection.execute(text("SELECT 1")).scalar_one() == 1


def test_database_metadata_has_stable_constraint_naming() -> None:
    assert Base.metadata.naming_convention["pk"] == "pk_%(table_name)s"
