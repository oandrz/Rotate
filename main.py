import os
import requests
import json
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
    url = "https://roundrobinbot-pr-2.onrender.com/group/add"
    request = {"name": group_name, "channelId": channel_id}
    response = requests.post(url, json=request)

    print(response)
    print("channel id is", channel_id)
    print("your group name is", group_name)

    if response == 200:
        say(f"Success add {group_name}")
    elif response == 400:
        say(f"{group_name} already exist in our database, please try with another user name")
    else:
        say(f"Sorry there's an unrecognizable error in my system, please wait until my engineer fix me")


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
@fastApp.post("/group/add")
async def add_new_group(group: schemas.GroupCreate, db: Session = Depends(get_db)):
    dbGroup = crud.getGroup(db, groupName=group.name, channelId=group.channelId)
    if dbGroup:
        raise HTTPException(status_code=400, detail="Group Already Exist")
    return crud.createGroup(db=db, group=group)


@fastApp.get("/group/{channel_id}", response_model=List[schemas.Group])
async def get_group_list(channel_id: str, db: Session = Depends(get_db)):
    print("channel Id: ", channel_id)
    dbGroup = crud.getGroupListInChannel(db=db, channelId=channel_id)
    if dbGroup:
        raise HTTPException(status_code=400, detail="No Group Exist")
    return dbGroup
