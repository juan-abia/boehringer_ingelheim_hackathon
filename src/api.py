import requests
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from src.agent import get_agent, agent_execute
import os

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/execute")
def execute(text: str, password: str):
    load_dotenv()

    agent = get_agent(keep_memory=False)
    if str(password) != str(os.environ["BB_API_KEY"]):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return agent_execute(agent, f"Please very very very very concise {text}", keep_memory=False)

@app.post("/query")
def query(text: str, password: str):
    load_dotenv()

    agent = get_agent(keep_memory=False)
    if str(password) != (os.environ["BB_API_KEY"]):
        raise HTTPException(status_code=401, detail="Unauthorized")
    alexa_response(text)
    return "successful: generating response"


def alexa_response(text: str):
    load_dotenv()

    agent = get_agent(keep_memory=False)
    response = agent_execute(agent, f"Please very very very very concise {text}", keep_memory=False)
    alexa_url = f"https://api-v2.voicemonkey.io/flows?token={os.environ['ALEXA_API_TOKEN']}&flow=1000&var-text_rx={response}"
    requests.post(alexa_url)
