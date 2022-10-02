"""
INSIDE my_project folder create a new virtualenv
- virtualenv env

Activate virtualenv
- source env/bin/activate

token=gIkuvaNzQIHg97ATvDxqgjtO
&team_id=T0001
&team_domain=example
&enterprise_id=E0001
&enterprise_name=Globular%20Construct%20Inc
&channel_id=C2147483705
&channel_name=test
&user_id=U2147483697
&user_name=Steve
&command=/weather
&text=94070
&response_url=https://hooks.slack.com/commands/1234/5678
&trigger_id=13345224609.738474920.8088930838d88f008e0
&api_app_id=A123456
"""
import os

from fastapi import FastAPI
from pydantic import BaseModel
from slack_bolt import App

app = FastAPI()
app_bolt = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

class Payload(BaseModel):
    text: str
    channel_name: str
    channel_id: str
    user_name: str
    user_id: str

@app.get("/")
async def root():
    return {"message": "Hello "}

@app.post("/addRotation")
async def addRotation(payload: Payload):
    return {
        "response_type": "in_channel",
        "text": payload.text
    }

@app_bolt.message("hello")
def message_hello(message, say):
    say(f"Hey there <@{message['user']}>!")

