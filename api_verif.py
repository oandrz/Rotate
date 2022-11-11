from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class RequestEvent(BaseModel):
    token: str
    challenge: str
    type: str


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/slack/events")
async def authorize(request: RequestEvent):
    return request.challenge
