from pydantic import BaseModel
from typing import (
    List, Optional
)
import json

class GroupBase(BaseModel):
    name: str
    channelId: str
    team_domain: str
    pickedSlackId: Optional[str] = None
    members: Optional[str] = None


class GroupCreate(GroupBase):
    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class GroupUpdate(GroupBase):
    pass


class Group(GroupBase):
    id: int

    class Config:
        orm_mode = True
