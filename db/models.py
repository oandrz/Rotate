from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from .database import Base

association_table = Table(
    "association_table",
    Base.metadata,
    Column("user_id", ForeignKey("user.id")),
    Column("rotation-group_id", ForeignKey("rotation-group.id")),
)


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    slackId = Column(String, unique=True)
    groups = relationship(
        "RotationGroup", secondary=association_table, back_populates="users"
    )


class RotationGroup(Base):
    __tablename__ = "rotation-group"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    channelId = Column(String)
    pickedSlackId = Column(String)
    users = relationship(
        "User", secondary=association_table, back_populates="groups"
    )
