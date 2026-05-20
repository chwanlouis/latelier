import enum
from sqlalchemy import Boolean, Column, ForeignKey, String, Integer, Enum
from sqlalchemy.sql import expression
from model.sql.base import SQLModelBaseClass


class UserLevelEnum(str, enum.Enum):
    BASIC = "BASIC"
    ADMIN = "ADMIN"


class UsersSQLModel(SQLModelBaseClass):
    __tablename__ = "users"

    username = Column(String(150), nullable=False, unique=True, index=True)
    password_hash = Column(String(1024), nullable=True)
    email = Column(String(320), nullable=False, unique=True, index=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    phone = Column(String(32), nullable=True)
    is_active = Column(Boolean, nullable=False, server_default=expression.true())
    user_level = Column(Enum(UserLevelEnum), nullable=False, server_default=expression.text(f"'{UserLevelEnum.BASIC.value}'"))
