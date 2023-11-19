import requests
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from src.agent import get_agent, agent_execute
import os
from pydantic import BaseModel
from urllib.parse import quote

class QueryInput(BaseModel):
    text: str
    password: str

app = FastAPI()
keep_memory=False

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/execute")
def execute(text: str, password: str):
    load_dotenv()

    agent = get_agent(keep_memory=keep_memory)
    if str(password) != str(os.environ["BB_API_KEY"]):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return agent_execute(agent=agent, user_input="Please be very very very very concise\n {text}", keep_memory=keep_memory)


@app.post("/query")
def query(data: QueryInput):
    load_dotenv()

    if str(data.password) != (os.environ["BB_API_KEY"]):
        raise HTTPException(status_code=401, detail="Unauthorized")
    response = alexa_response(data.text)
    return f"Generated response: {response}"


def alexa_response(text: str):
    load_dotenv()
    keep_memory=False
    agent = get_agent(keep_memory=keep_memory)
    response = agent_execute(agent=agent, user_input=f"Please be very very very very concise {text}", keep_memory=keep_memory)

    encoded_response = quote(response)

    alexa_url = f"https://api-v2.voicemonkey.io/flows?token={os.environ['ALEXA_API_TOKEN']}&flow=1000"
    headers = {'Content-Type': 'application/json'}
    data = {"var-text_rx": response}
    req_response = requests.post(alexa_url, headers=headers, json=data)
    print(alexa_url)
    print(response)
    print(req_response.status_code)
    print(req_response.text)
    return response
