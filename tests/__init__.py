import uuid, enum
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String
from sqlalchemy_utils.types.choice import ChoiceType
from sqlalchemy.dialects.postgresql import UUID


Base = declarative_base()


class StatusEnum(enum.Enum):
    enable = "enable"
    disable = "disable"


class Table(Base):
    __tablename__ = "table"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    status = Column(ChoiceType(StatusEnum, impl=String()))