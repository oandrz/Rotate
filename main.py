import os
import requests
import json
from slack_bolt import App
from fastapi import FastAPI, Request, Depends, HTTPException
from pydantic import BaseModel
from slack_bolt.adapter.fastapi import SlackRequestHandler

from typing import List
from sqlalchemy.orm import Session
from db import crud, models, schemas
from db.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

HOST_URL = os.environ["API_HOST"]
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
    if "text" not in command:
        say("Please put the parameter, to add rotation you can do it like this `/add-rotation [group name]`")
        return

    group_name = command['text']
    channel_id = command['channel_id']

    url = HOST_URL + "/group/add"
    request = {"name": group_name, "channelId": channel_id}
    response = requests.post(url, json=request)

    if response.status_code == requests.codes.ok:
        say(f"Success add {group_name}")
    elif response.status_code == 400:
        say(f"{group_name} already exist in our database")
    else:
        say(f"Sorry there's an unrecognizable error in my system, please wait until my engineer fix me")


@app.command("/add-member")
def add_member(ack, say, command):
    ack()
    if "text" not in command or len(command["text"].split()) <= 1:
        say("Please put the parameter, to add member you can do it like this `/add-member [group name] [member1,...]`")
        return

    channel_id = command['channel_id']
    command_text = command['text'].split()

    group_name = command_text[0]
    response_group = request_group(channel_id, group_name, say)

    group = json.loads(response_group.text)
    picked_member = group['pickedSlackId']
    members = group['members']

    members_request = update_member_list(current_members=members, new_members=command_text)

    picked_member_request = ""
    if picked_member is None:
        picked_member_request = members_request.split(',')[0]

    response = request_update_member(
        channel_id=channel_id,
        group_name=group_name,
        picked_member=picked_member_request,
        members=members_request
    )

    if response.status_code == 400:
        say(f"{group_name} doesn't exist in our database")
    elif response.status_code == requests.codes.ok:
        say(f"Add member success")
    else:
        say(f"Sorry there's an unrecognizable error in my system, please wait until my engineer fix me")


def request_group(channel_id: str, group_name: str, say):
    url = HOST_URL + "/group"

    query_params = {"channel_id": channel_id, "group_name": group_name}
    response = requests.get(url=url, params=query_params)

    if response.status_code == 400:
        say(f"{group_name} doesn't exist in our database")
    elif response.status_code == requests.codes.ok:
        return response
    else:
        say(f"Sorry there's an unrecognizable error in my system, please wait until my engineer fix me")


def request_update_member(
    channel_id: str,
    group_name: str,
    picked_member: str,
    members: str
):
    url = HOST_URL + "/group/member"

    request_body = {"name": group_name, "channelId": channel_id, "pickedSlackId": picked_member,
                    "members": members}
    response = requests.put(url, json=request_body)

    return response


def update_member_list(
    current_members: str,
    new_members,
):
    modified_members = ""
    count = 0

    if current_members is not None:
        count = len(current_members.split(","))
        modified_members = current_members

    for i in range(1, len(new_members)):
        if new_members[i] in modified_members:
            continue
        count += 1
        if count > 1:
            modified_members += ','
        modified_members += new_members[i]

    return modified_members


@app.command("/list-member")
def list_member(ack, say, command):
    ack()

    if "text" not in command:
        say("Please put the parameter, to list member of the group you can do it like this `/list-member [group name]`")
        return

    command_text = command['text'].split()
    channel_id = command['channel_id']
    group_name = command_text[0]
    response = request_group(channel_id=channel_id, group_name=group_name, say=say)
    if response is not None:
        group = json.loads(response.text)
        members = group['members'].split(",")
        count = 0
        for member in members:
            count += 1
            say(f"Group member number {count}: <{member}>!")


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
            say(f"Here are the group that I could found in this channel: `{text}`")
    elif response.status_code == 400:
        say(f"We don't found any rotation group, please create a new one first.")
    else:
        say(f"Sorry there's an unrecognizable error in my system, please wait until my engineer fix me")


@app.command("/peek-current")
def peek_current_turn(ack, say, command):
    ack()

    if "text" not in command:
        say("Wrong formatting, to see current turn of the group you can do it like this` /peek-current [group name]`")
        return

    command_text = command['text'].split()
    channel_id = command['channel_id']
    group_name = command_text[0]

    response = request_group(channel_id=channel_id, group_name=group_name, say=say)

    if response is not None:
        group = json.loads(response.text)
        if "pickedSlackId" not in group or group["pickedSlackId"] is None or len(group["pickedSlackId"]) == 0:
            say(f"You don't have selected member for this rotation, please assign one by using `/rotate [group name]`")
        else:
            picked_member = group["pickedSlackId"]
            say(f"Current turn is <{picked_member}>!")


@app.command("/rotate")
def rotate_member(ack, say, command):
    ack()

    if "text" not in command:
        say("Wrong formatting, to see current turn of the group you can do it like this `/peek-current [group name]`")
        return

    command_text = command['text'].split()
    channel_id = command['channel_id']
    group_name = command_text[0]

    response = request_group(channel_id=channel_id, group_name=group_name, say=say)

    if response is not None:
        updated_members = group_lru(response, say)
        updated_picked_member = updated_members.split(",")[0]

        response = request_update_member(
            channel_id=channel_id,
            group_name=group_name,
            picked_member=updated_picked_member,
            members=updated_members
        )

        if response.status_code == 400:
            say(f"{group_name} doesn't exist in our database")
        elif response.status_code == requests.codes.ok:
            say(f"<{updated_picked_member}>! it's your turn now")
        else:
            say(f"Sorry there's an unrecognizable error in my system, please wait until my engineer fix me")


def group_lru(response, say):
    updated_members = ""

    group = json.loads(response.text)
    if "members" not in group or len(group["members"]) == 0:
        say(f"Please add the member of this rotation first")
        return

    members = group["members"].split(",")
    move_back_member = members[0]

    for i in range(1, len(members)):
        updated_members += members[i]
        if len(members) - 1 - i > 0:
            updated_members += ','

    return updated_members + ',' + move_back_member


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
async def add_member_command(req: Request):
    return await app_handler.handle(req)


@fastApp.post("/slack/list-member")
async def list_member_command(req: Request):
    return await app_handler.handle(req)


@fastApp.post("/slack/list-rotation")
async def list_rotation_command(req: Request):
    return await app_handler.handle(req)


@fastApp.post("/slack/peek-current")
async def peek_current_command(req: Request):
    return await app_handler.handle(req)


@fastApp.post("/slack/rotate")
async def rotate_command(req: Request):
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
    db_group = crud.getGroup(db, groupName=group.name, channelId=group.channelId)
    if db_group is None:
        raise HTTPException(status_code=400, detail="No Group Exist")
    return crud.updateGroup(db=db, group=group)


@fastApp.get("/group", response_model=schemas.Group)
async def get_specific_group(channel_id: str, group_name: str, db: Session = Depends(get_db)):
    db_group = crud.getGroup(db, groupName=group_name, channelId=channel_id)
    if db_group is None:
        raise HTTPException(status_code=400, detail="No Group Exist")
    return db_group

