from typing import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from albatross.models import Base
from albatross.models.camera import Camera
from albatross.models.lens import Lens
from albatross.models.recommendations import Recommendations
from albatross.repository.base_repository import AlbatrossRepository


@pytest.fixture(scope="session")
def in_memory_db() -> Generator[sessionmaker[Session], None, None]:
    # Create an in-memory SQLite database
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)  # Create all tables
    session: sessionmaker[Session] = sessionmaker(bind=engine)

    # Provide the session factory to the test
    yield session

    # Teardown: Dispose of the engine
    engine.dispose()


@pytest.fixture(autouse=True)
def repository(in_memory_db: sessionmaker[Session]) -> AlbatrossRepository:
    # Create an instance of the repository with the in-memory database
    return AlbatrossRepository(session=in_memory_db)


@pytest.fixture(autouse=True)
def teardown_database(repository: AlbatrossRepository) -> None:
    # Clear the database before each test
    with repository.session_scope() as session:
        session.query(Camera).delete()
        session.query(Lens).delete()
        session.query(Recommendations).delete()
        session.commit()
