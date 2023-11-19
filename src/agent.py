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


def agent_execute(agent, user_input: str, keep_memory: bool = True):
    response = agent.run(str(get_prompt(keep_memory) + user_input + "\nAgent:"))
    cleaned_response = re.sub(r'{[^}]*}', '', response)
    return cleaned_response


def get_agent(keep_memory: bool = True):
    llm = get_llm()
    tools = [FindRecipesByQuery(), GetRecipeInfo()]

    if keep_memory:
        memory = ConversationBufferMemory(memory_key="memory", return_messages=True)
        agent_kwargs = {
            "extra_prompt_messages": [MessagesPlaceholder(variable_name="memory")],
        }

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
            verbose=DEBUG,
            prompt=get_prompt(keep_memory)
        )

    return agent


def get_prompt(keep_memory: bool = True):
    prompts = {"objectives": {}, "rules": {}, "peer_reviewed_papers": {}, "few_shot_learning": {}}
    for prompt_file_name in prompts:
        with open(os.path.join(SRC_DIR, "data", "prompts", f"{prompt_file_name}.txt"), "r", encoding="utf8") as f:
            prompts[prompt_file_name] = f.read()

    template = ("System: Eres un asistente cuyo objetivo es:\n"
                f"```\n{prompts['objectives']}\n```\n"
                "System: Estas son tus normas, cúmplelas en todo momento"
                f"```\n{prompts['rules']}\n```\n" 
                "System: Este es el mejor conocimiento cientifico sobre dietas en pacientes con obesidad:\n"
                f"```\n{prompts['peer_reviewed_papers']}\n```\n"
                "System: Aqui tienes ejemplos de la interaccion con el usuario\n"
                f"```\n{prompts['few_shot_learning']}\n```\n"
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
    keep_memory = True
    my_agent = get_agent(keep_memory=keep_memory)

    while True:
        user_text = input("Your input:")
        response = agent_execute(my_agent, user_text, keep_memory=keep_memory)
        print(response)
