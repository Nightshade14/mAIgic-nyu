from sqlalchemy import Integer, create_engine, Column, String, Enum
import enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()


class ItemType(enum.StrEnum):
    gmail = enum.auto()


class Item(Base):
    __tablename__ = "items"

    type = Column(Enum(ItemType), nullable=False, primary_key=True)  # gmail for now
    id = Column(String, primary_key=True)
    slack_channel = Column(String)
    slack_thread = Column(String)
    content = Column(String)


class Chat(Base):
    __tablename__ = "chats"

    seq = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(Enum(ItemType), nullable=False) # this and the next one is a foreign key to Item
    id = Column(String)
    role = Column(String)
    content = Column(String)


class DB:
    def __init__(self) -> None:
        self.engine = create_engine("sqlite:///maigic.db", echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
