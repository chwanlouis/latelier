from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class SQLModelBaseClass(Base):
    __abstract__ = True

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def __repr__(self):
        return f"<{self.__class__.__name__}(date={self.date}, symbol={self.symbol})>"