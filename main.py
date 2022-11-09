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

/add-rotation named

slackbot token
export SLACK_BOT_TOKEN=xoxb-1002662208229-4200810073063-YaBvin8958dRWlEqiQ4nGj7c
export SLACK_APP_TOKEN=xapp-1-A046B5T3H26-4208778319110-bb7492cdd72be7bc2cbfd36dea6fc992d59afd482e4a16a4ba8bff91a2100d35
"""
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from collections import deque

app = App(token=os.environ["SLACK_BOT_TOKEN"])

db = dict()


@app.command("/add-rotation")
def add_group(ack, say, command):
    ack()
    groupName = command['text']
    print("your group name is", groupName)
    q = deque()
    isKeyExist = groupName in db
    if isKeyExist:
        q = db[groupName]
    db[groupName] = q
    say(f"Success add {groupName}")


@app.command("/add-member")
def add_member(ack, say, command):
    ack()
    commandText = command['text'].split()
    groupName = commandText[0]
    isKeyExist = groupName in db
    if not isKeyExist:
        say(f"Group doesn't exist")
    else:
        q = db[groupName]
        numberOfMember = len(commandText)
        for i in range(1, numberOfMember):
            q.append(commandText[i])
        say(f"Add member success")


@app.command("/list-member")
def list_member(ack, say, command):
    ack()
    commandText = command['text'].split()
    groupName = commandText[0]
    isKeyExist = groupName in db
    if not isKeyExist:
        say(f"Group doesn't exist")
    else:
        q = db[groupName]

        count = 1
        for member in q:
            say(f"Group member number {count}: <{member}>!")
            count += 1


@app.command("/list-rotation")
def list_rotation(ack, say):
    ack()
    if len(db) == 0:
        say("You don't have saved rotation")
    else:
        text = ''
        count = 0
        for key in db.keys():
            count += 1
            if count > 1:
                text += ', '
            text += key
        say(f"Here are the list of your group: {text}")


@app.command("/peek-current")
def peek_current_turn(ack, say, command):
    ack()
    commandText = command['text'].split()
    groupName = commandText[0]
    isKeyExist = groupName in db
    if not isKeyExist:
        say("Group doesn't exist")
    else:
        q = db[groupName]
        currentTurn = q[0]

        if currentTurn is not None:
            say(f"Current turn is <{currentTurn}>!")


@app.command("/rotate")
def rotate_member(ack, say, command):
    ack()
    commandText = command['text'].split()
    groupName = commandText[0]
    isKeyExist = groupName in db
    if not isKeyExist:
        say("Group doesn't exist")
    else:
        q = db[groupName]
        rotated = q.popleft()
        current = q[0]
        q.append(rotated)

        if current is not None:
            say(f"Current turn is <{current}>!")


if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
