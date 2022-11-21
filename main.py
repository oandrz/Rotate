import os
from slack_bolt import App
from collections import deque
from fastapi import FastAPI, Request, Depends, HTTPException
from pydantic import BaseModel
from slack_bolt.adapter.fastapi import SlackRequestHandler

from typing import List
from sqlalchemy.orm import Session
from db import crud, models, schemas
from db.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = App(
    token=os.environ["SLACK_BOT_TOKEN"],
    signing_secret=os.environ["SLACK_SIGNING_SECRET"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.command("/add-rotation")
def add_group(ack, say, command):
    ack()
    group_name = command['text']
    channel_id = command['channel_id']
    print("channel id is", channel_id)
    print("your group name is", group_name)
    addNewGroup(
        group=schemas.GroupCreate(
            name=group_name,
            channel_id=channel_id
        )
    )
    say(f"Success add {group_name}")


@app.command("/add-member")
def add_member(ack, say, command):
    ack()
    commandText = command['text'].split()
    # groupName = commandText[0]
    # isKeyExist = groupName in db
    # if not isKeyExist:
    #     say(f"Group doesn't exist")
    # else:
    #     q = db[groupName]
    #     numberOfMember = len(commandText)
    #     for i in range(1, numberOfMember):
    #         q.append(commandText[i])
    say(f"Add member success")


@app.command("/list-member")
def list_member(ack, say, command):
    ack()
    # commandText = command['text'].split()
    # groupName = commandText[0]
    # isKeyExist = groupName in db
    # if not isKeyExist:
    #     say(f"Group doesn't exist")
    # else:
    #     q = db[groupName]
    #
    #     count = 1
    #     for member in q:
    #         say(f"Group member number {count}: <{member}>!")
    #         count += 1


@app.command("/list-rotation")
def list_rotation(ack, say):
    ack()
    # if len(db) == 0:
    #     say("You don't have saved rotation")
    # else:
    #     text = ''
    #     count = 0
    #     for key in db.keys():
    #         count += 1
    #         if count > 1:
    #             text += ', '
    #         text += key
    #     say(f"Here are the list of your group: {text}")


@app.command("/peek-current")
def peek_current_turn(ack, say, command):
    ack()
    commandText = command['text'].split()
    # groupName = commandText[0]
    # isKeyExist = groupName in db
    # if not isKeyExist:
    #     say("Group doesn't exist")
    # else:
    #     q = db[groupName]
    #     currentTurn = q[0]
    #
    #     if currentTurn is not None:
    #         say(f"Current turn is <{currentTurn}>!")


@app.command("/rotate")
def rotate_member(ack, say, command):
    ack()
    commandText = command['text'].split()
    # groupName = commandText[0]
    # isKeyExist = groupName in db
    # if not isKeyExist:
    #     say("Group doesn't exist")
    # else:
    #     q = db[groupName]
    #     rotated = q.popleft()
    #     current = q[0]
    #     q.append(rotated)
    #
    #     if current is not None:
    #         say(f"Current turn is <{current}>!")


# FastAPI

fastApp = FastAPI()
app_handler = SlackRequestHandler(app)


class RequestEvent(BaseModel):
    token: str
    challenge: str
    type: str


@fastApp.get("/")
async def root():
    return {"message": "Hello World"}


@fastApp.post("/slack/events")
async def authorize(request: RequestEvent):
    return request.challenge


@fastApp.post("/slack/add-rotation")
async def add_rotation_command(req: Request):
    return await app_handler.handle(req)


@fastApp.post("/slack/add-member")
async def add_rotation_command(req: Request):
    return await app_handler.handle(req)


@fastApp.post("/slack/list-member")
async def list_member_command(req: Request):
    return await app_handler.handle(req)


@fastApp.post("/slack/list-rotation")
async def list_rotation_command(req: Request):
    return await app_handler.handle(req)


@fastApp.post("/slack/peek-current")
async def list_rotation_command(req: Request):
    return await app_handler.handle(req)


@fastApp.post("/slack/rotate")
async def list_rotation_command(req: Request):
    return await app_handler.handle(req)


# DB
def addNewGroup(group: schemas.GroupCreate, db: Session = Depends(get_db())):
    dbGroup = crud.getGroup(db, groupName=group.name, channelId=group.channelId)
    if dbGroup:
        raise HTTPException(status_code=400, detail="Group Already Exist")
    return crud.createGroup(db=db, group=group)
