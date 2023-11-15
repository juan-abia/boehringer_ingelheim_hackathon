import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain import LLMChain, PromptTemplate
from langchain.memory import ConversationTokenBufferMemory, ChatMessageHistory


def get_llm():
    load_dotenv()

    model = ChatOpenAI(model_name="gpt-4-1106-preview")
    return model


def get_chain():
    chain = LLMChain(
        llm=get_llm(),
        prompt=get_prompt(),
        verbose=True,
        memory=ConversationTokenBufferMemory(
            llm=ChatOpenAI(), max_token_limit=4000
        ),
    )

    return chain


def get_prompt():
    # with open(os.path.join(SRC_DIR, "data", "kpis.txt"), "r", encoding="utf8") as f:
    #     kpis = f.read()
    #
    # with open(os.path.join(SRC_DIR, "data", "base.txt"), "r", encoding="utf8") as f:
    #     base = f.read()

    template = ("System: Eres un asistente dispuesto a ayudar"
                "Aqui empieza la interaccion con el usuario:\n"
                "{history}\n"
                "Human: {user_prompt}")

    prompt = PromptTemplate(
        input_variables=["user_prompt", "history"], template=template
    )

    return prompt


if __name__ == "__main__":
    chain = get_chain()

    while True:
        user_text = input("Your input:")
        response = chain.predict(user_prompt=user_text)
        print(response)