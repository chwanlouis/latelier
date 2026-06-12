from enum import Enum
from sqlalchemy import Column, String, Boolean
from sqlalchemy import Enum as SQLEnum
from module.core.model.sql.base import SQLModelBaseClass


class UserGroupEnum(str, Enum):
    admin = "admin"
    basic = "basic"


class UserSQLModel(SQLModelBaseClass):
    __tablename__ = "users"

    username = Column(String(50), nullable=False, unique=True, index=True)
    email = Column(String(100), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    user_group = Column(
        SQLEnum(UserGroupEnum, name="user_level_enum", inherit_schema=True),
        nullable=False,
        default=UserGroupEnum.basic,
        index=True
    )
    is_active = Column(Boolean, nullable=False, server_default="true")
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    phone_number = Column(String(30), nullable=True)
    whatsapp_number = Column(String(30), nullable=True)

    @property
    def full_name(self) -> str:
        fn = self.first_name or ""
        ln = self.last_name or ""
        return f"{fn} {ln}".strip()

    def __repr__(self):
        return (
            f"<UserSQLModel(id={self.id}, username='{self.username}', "
            f"name='{self.full_name}', org_id={self.organisation_id})>"
        )
