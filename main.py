import os
import requests
import json
import logging
from slack_bolt import App
from fastapi import FastAPI, Request, Depends, HTTPException
from pydantic import BaseModel
from slack_bolt.adapter.fastapi import SlackRequestHandler

from typing import List
from sqlalchemy.orm import Session
from db import crud, models, schemas
from db.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

HOST_URL = "https://roundrobinbot-pr-3.onrender.com"
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
    url = HOST_URL + "/group/add"
    request = {"name": group_name, "channelId": channel_id}
    response = requests.post(url, json=request)

    if response.status_code == requests.codes.ok:
        say(f"Success add {group_name}")
    elif response.status_code == 400:
        say(f"{group_name} already exist in our database, please try with another user name")
    else:
        say(f"Sorry there's an unrecognizable error in my system, please wait until my engineer fix me")


@app.command("/add-member")
def add_member(ack, say, command):
    ack()
    channel_id = command['channel_id']
    command_text = command['text'].split()

    group_name = command_text[0]
    response_group = request_group(channel_id, group_name, say)

    group = json.loads(response_group.text)
    picked_member = group['pickedSlackId']
    members = group['members']

    request_update_member(
        channel_id=channel_id,
        group_name=group_name,
        picked_member=picked_member,
        new_members=command_text,
        current_members=members,
        say=say
    )

    request = {""}
    # if not isKeyExist:
    #     say(f"Group doesn't exist")
    # else:
    #     q = db[groupName]
    #     numberOfMember = len(commandText)
    #     for i in range(1, numberOfMember):
    #         q.append(commandText[i])



def request_group(channel_id: str, group_name: str, say):
    url = HOST_URL + "/group"
    query_params = {"channel_id": channel_id, "group_name": group_name}
    response = requests.get(url=url, params=query_params)
    if response.status_code == 400:
        say(f"{group_name} doesn't exist in our database, please try with another user name")
    elif response.status_code == requests.codes.ok:
        return response
    else:
        say(f"Sorry there's an unrecognizable error in my system, please wait until my engineer fix me")


def request_update_member(
    channel_id: str,
    group_name: str,
    picked_member: str,
    current_members: str,
    new_members: List[str],
    say
):
    members_request = update_member_list(current_members, new_members)
    picked_member_request = ""
    if picked_member is None:
        picked_member_request = members_request.split(',')[0]

    print("group name is:", members_request)
    print("group name is:", picked_member_request)
    url = HOST_URL + "/group/member"
    request_body = {"name": group_name, "channelId": channel_id, "pickedSlackId": picked_member_request, "members": members_request}
    response = requests.put(url, json=request_body)

    if response.status_code == 400:
        say(f"{group_name} doesn't exist in our database, please try with another name")
    elif response.status_code == requests.codes.ok:
        say(f"Add member success")
    else:
        say(f"Sorry there's an unrecognizable error in my system, please wait until my engineer fix me")

def update_member_list(
    current_members: str,
    new_members: List[str],
):
    modified_members = current_members
    count = 0

    print("member is", new_members)
    print("current is", current_members)
    for i in range(1, len(new_members) - 1):
        count += 1
        if count > 1:
            modified_members += ','
        modified_members += new_members[i]

    print("Current modified member is", modified_members)

    return modified_members

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
def list_rotation(ack, say, command):
    ack()
    channel_id = command['channel_id']
    url = HOST_URL + "/group/" + channel_id
    response = requests.get(url)

    if response.status_code == requests.codes.ok:
        group_list = json.loads(response.text)
        if len(group_list) == 0:
            say(f"We don't found any rotation group, please create a new one first.")
        else:
            text = ""
            count = 0
            for group in group_list:
                count += 1
                if count > 1:
                    text += ', '
                text += group['name']
            say(f"Here are the group that I could found in this channel: {text}")
    elif response.status_code == 400:
        say(f"We don't found any rotation group, please create a new one first.")
    else:
        say(f"Sorry there's an unrecognizable error in my system, please wait until my engineer fix me")


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
    db_group = crud.getGroup(db, groupName=group.name, channelId=group.channelId)
    if db_group:
        raise HTTPException(status_code=400, detail="Group Already Exist")
    return crud.createGroup(db=db, group=group)


@fastApp.get("/group/{channel_id}", response_model=List[schemas.Group])
async def get_group_list(channel_id: str, db: Session = Depends(get_db)):
    db_group = crud.getGroupListInChannel(db=db, channelId=channel_id)
    if db_group is None:
        raise HTTPException(status_code=400, detail="No Group Exist")
    return db_group


@fastApp.put("/group/member")
async def update_group_to_add_member(group: schemas.GroupUpdate, db: Session = Depends(get_db)):
    print("group members", group.members)

    print("picked group member", group.pickedSlackId)
    db_group = crud.getGroup(db, groupName=group.name, channelId=group.channelId)
    if db_group is None:
        raise HTTPException(status_code=400, detail="No Group Exist")
    return crud.updateGroup(db=db, group=group)


@fastApp.get("/group",  response_model=schemas.Group)
async def get_specific_group(channel_id: str, group_name: str, db: Session = Depends(get_db)):
    db_group = crud.getGroup(db, groupName=group_name, channelId=channel_id)
    if db_group is None:
        raise HTTPException(status_code=400, detail="No Group Exist")
    return db_group
