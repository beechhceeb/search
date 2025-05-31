from uuid import UUID

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    id: None | UUID = None
    pass
