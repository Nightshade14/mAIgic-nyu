"""TODO: Add docstring."""

import enum

from sqlalchemy import Column, Enum, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class ItemType(enum.StrEnum):
    """TODO: Add docstring."""

    gmail = enum.auto()


class Item(Base):
    """TODO: Add docstring."""

    __tablename__ = "items"

    type = Column(Enum(ItemType), nullable=False, primary_key=True)
    id = Column(String, primary_key=True)
    slack_channel = Column(String)
    slack_thread = Column(String)
    content = Column(String)


class Chat(Base):
    """TODO: Add docstring."""

    __tablename__ = "chats"

    seq = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(
        Enum(ItemType), nullable=False
    )  # this and the next one is a foreign key to Item
    id = Column(String)
    role = Column(String)
    content = Column(String)


class DB:
    """TODO: Add docstring."""

    def __init__(self) -> None:
        """TODO: Add docstring."""
        self.engine = create_engine("sqlite:///maigic.db", echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
