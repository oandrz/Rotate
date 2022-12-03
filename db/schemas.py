from pydantic import BaseModel
from typing import (
    List, Optional
)


class GroupBase(BaseModel):
    name: str
    channelId: str
    team_domain: str
    pickedSlackId: Optional[str] = None
    members: Optional[str] = None


class GroupCreate(GroupBase):
    pass


class GroupUpdate(GroupBase):
    pass


class Group(GroupBase):
    id: int

    class Config:
        orm_mode = True
