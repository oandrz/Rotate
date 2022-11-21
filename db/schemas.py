from pydantic import BaseModel
from typing import (
    List, Optional
)


class UserBase(BaseModel):
    slackId: str


class GroupBase(BaseModel):
    name: str
    channelId: str
    pickedSlackId: Optional[str] = None


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    groups: List[GroupBase] = []

    class Config:
        orm_mode = True


class GroupCreate(GroupBase):
    pass


class Group(GroupBase):
    id: int
    users: List[UserBase] = []

    class Config:
        orm_mode = True