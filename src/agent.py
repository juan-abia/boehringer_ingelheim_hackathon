import os
import re
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentType, initialize_agent
from langchain.prompts import MessagesPlaceholder

from src import SRC_DIR, DEBUG
from src.recipe_api import FindRecipesByQuery, GetRecipeInfo


def get_llm():
    load_dotenv()

    model = ChatOpenAI(model_name="gpt-4-1106-preview")
    return model


def agent_execute(agent, user_input, keep_memory: bool = True):
    response = agent.run(get_prompt(keep_memory) + user_input + "\nAgent:")
    cleaned_response = re.sub(r'\s*{[^}]*}\s*', '', response)
    return cleaned_response


def get_agent(keep_memory: bool = True):
    llm = get_llm()
    tools = [FindRecipesByQuery(), GetRecipeInfo()]
    agent_kwargs = {
        "extra_prompt_messages": [MessagesPlaceholder(variable_name="memory")],
    }
    memory = ConversationBufferMemory(memory_key="memory", return_messages=True)

    if keep_memory:
        agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.OPENAI_FUNCTIONS,
            agent_kwargs=agent_kwargs,
            verbose=DEBUG,
            memory=memory,
            prompt=get_prompt(keep_memory)
        )
    else:
        agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.OPENAI_FUNCTIONS,
            agent_kwargs=agent_kwargs,
            verbose=DEBUG,
            memory=memory,
            prompt=get_prompt(keep_memory)
        )

    return agent


def get_prompt(keep_memory: bool = True):
    with open(os.path.join(SRC_DIR, "data", "prompts", "objectives.txt"), "r", encoding="utf8") as f:
        objectives = f.read()

    with open(os.path.join(SRC_DIR, "data", "prompts", "peer_reviewed_papers.txt"), "r", encoding="utf8") as f:
        peer_reviewed_papers = f.read()

    with open(os.path.join(SRC_DIR, "data", "prompts", "few_shot_learning.txt"), "r", encoding="utf8") as f:
        few_shot_learning = f.read()

    template = ("System: Eres un asistente cuyo objetivo es:\n"
                f"```\n{objectives}\n```\n"
                "System: Este es el mejor conocimiento cientifico sobre dietas en pacientes con obesidad:\n"
                f"```\n{peer_reviewed_papers}\n```\n"
                "System: Aqui tienes ejemplos de la interaccion con el usuario\n"
                f"```\n{few_shot_learning}\n```\n"
                "Aqui empieza la interaccion con el usuario:\n"
                "{memory}\n"
                "Human:")

    if keep_memory:
        prompt = PromptTemplate(
            input_variables=["memory"], template=template
        )
        return prompt
    else:
        return template




if __name__ == "__main__":
    agent = get_agent()

    while True:
        user_text = input("Your input:")
        response = agent_execute(agent, user_text)
        print(response)
