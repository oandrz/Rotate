from sqlalchemy.orm import Session
from . import models, schemas


def getGroupListInChannel(db: Session, channelId: str):
    return db.query(models.RotationGroup).filter(models.RotationGroup.channelId == channelId).first()


def getMemberInGroup(db: Session, groupName: str, channelId: str):
    return getGroup(db, groupName, channelId).users


def getPickedMember(db: Session, groupName: str, channelId: str):
    return getGroup(db, groupName, channelId).pickedSlackId


def getGroup(db: Session, groupName: str, channelId: str):
    return db.query(models.RotationGroup).filter(
        models.RotationGroup.name == groupName and models.RotationGroup.channelId == channelId
    ).first()


def createUser(db: Session, user: schemas.UserCreate):
    db_user = models.User(slackId=user.slackId)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def createGroup(db: Session, group: schemas.GroupCreate):
    db_group = models.RotationGroup(name=group.name, channelId=group.channelId, pickedSlackId=group.pickedSlackId)
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group
