import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.agents import AgentExecutor
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentType, initialize_agent
from langchain.prompts import MessagesPlaceholder

from src import SRC_DIR, DEBUG
from src.api import FindRecipesByQuery


def get_llm():
    load_dotenv()

    model = ChatOpenAI(model_name="gpt-4-1106-preview")
    return model


def agent_execute(agent, user_input):
    return agent.run(get_prompt() + user_input)


def get_agent():
    llm = get_llm()
    tools = [FindRecipesByQuery()]
    agent_kwargs = {
        "extra_prompt_messages": [MessagesPlaceholder(variable_name="memory")],
    }
    memory = ConversationBufferMemory(memory_key="memory", return_messages=True)

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        agent_kwargs=agent_kwargs,
        verbose=DEBUG,
        memory=memory,
        prompt=get_prompt()
    )

    return agent


def get_prompt():
    with open(os.path.join(SRC_DIR, "data", "prompts", "objectives.txt"), "r", encoding="utf8") as f:
        objectives = f.read()

    with open(os.path.join(SRC_DIR, "data", "prompts", "peer_reviewed_papers.txt"), "r", encoding="utf8") as f:
        peer_reviewed_papers = f.read()

    with open(os.path.join(SRC_DIR, "data", "prompts", "peer_reviewed_papers.txt"), "r", encoding="utf8") as f:
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

    prompt = PromptTemplate(
        input_variables=["memory"], template=template
    )

    return str(prompt)


if __name__ == "__main__":
    agent = get_agent()

    while True:
        user_text = input("Your input:")
        response = agent_execute(agent, user_text)
        print(response)
