from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, Integer, func, ForeignKey
from sqlalchemy.orm import declared_attr


Base = declarative_base()


class SQLModelBaseClass(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now(),
                        index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


class UserMixin:
    @declared_attr
    def user_id(cls):
        return Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

