from sqlalchemy import Column, Integer, String
from .database import Base


class RotationGroup(Base):
    __tablename__ = "rotation-group"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    channelId = Column(String)
    pickedSlackId = Column(String)
    members = Column(String)
