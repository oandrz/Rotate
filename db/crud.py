from sqlalchemy.orm import Session
from . import models, schemas


def getGroupListInChannel(db: Session, channelId: str):
    return db.query(models.RotationGroup).filter(models.RotationGroup.channelId == channelId).all()


def getMemberInGroup(db: Session, groupName: str, channelId: str):
    return getGroup(db, groupName, channelId).members


def getPickedMember(db: Session, groupName: str, channelId: str):
    return getGroup(db, groupName, channelId).pickedSlackId


def getGroup(db: Session, groupName: str, channelId: str, team_domain: str):
    return db.query(models.RotationGroup).filter(
        models.RotationGroup.name == groupName and models.RotationGroup.channelId == channelId
    ).first()


def createGroup(db: Session, group: schemas.GroupCreate):
    db_group = models.RotationGroup(name=group.name, channelId=group.channelId)
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group


def updateGroup(db: Session, group: schemas.GroupUpdate):
    db_group = getGroup(db=db, groupName=group.name, channelId=group.channelId)
    for var, value in vars(group).items():
        print("the value of var is" + var + " and the value is: " + value)
        setattr(db_group, var, value) if value else None
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group
