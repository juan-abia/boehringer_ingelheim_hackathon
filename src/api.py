import json
import logging
import os

import requests
from dotenv import load_dotenv
from langchain.tools import BaseTool
from langchain.agents import AgentType, initialize_agent
from src import DEBUG
from langchain.chat_models import ChatOpenAI

load_dotenv()


class FindRecipesByIngredients(BaseTool):
    name = "find_recipes_by_ingredients"
    description = ("Useful for when you need find a list of recipes based on ingredients to use and ingredients to not use"
                   "parameters:"
                   "    include_ingredients: comma separated str of ingredients (in english) to use. the ingredients should ALWAYS be translated to english"
                   "    exclude_ingredients: comma separated str of ingredients (in english) to NOT use. the ingredients  should ALWAYS be translated to english")

    def _run(self, include_ingredients: str = "", exclude_ingredients: str = "") -> str:
        api_key = os.environ["SPOONACULAR_API_KEY"]
        base_url = "https://api.spoonacular.com/recipes/complexSearch"
        params = {
            'apiKey': api_key,
            'number': 7,
            'ranking': 1,
            'includeIngredients': include_ingredients,
            'excludeIngredients': exclude_ingredients,
            'ignorePantry': False,
            'sort': 'healthiness',
            'addRecipeInformation': False,
            'addRecipeNutrition': False
        }

        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            return self.format_find_recipes_by_ingredients_output(response)
        else:
            logging.error(f"Error: {response.status_code}, {response.text}")
            print("Error:", response.status_code, response.text)
            return ""

    async def _arun(self) -> str:
        raise NotImplementedError("custom_search does not support async")

    @staticmethod
    def format_find_recipes_by_ingredients_output(response):
        return json.dumps([{'id': recipe['id'], 'title': recipe['title']} for recipe in response.json()['results']], indent=4)


class FindRecipesByQuery(BaseTool):
    name = "find_recipes_by_query"
    description = ("Useful for when you need find a list of recipes."
                   "Just provide the query of the recipes you want to look for."
                   "Only use this tool when you are looking for new recipes")

    @staticmethod
    def get_llm():
        load_dotenv()

        model = ChatOpenAI(model_name="gpt-4-1106-preview")
        return model

    def _run(self, query) -> str:
        prompt = ("System: You are an assistant, your task is to translate a query of a type of recipes into an actual list of"
                  "recipes consisting of an id and the title of the recipe. Very important. The query you receive is in SPANISH,"
                  "but all the tools you have available are in english")
        tools = [FindRecipesByIngredients()]
        agent = initialize_agent(
            llm=self.get_llm(),
            verbose=DEBUG,
            tools=tools,
            agent=AgentType.OPENAI_MULTI_FUNCTIONS
        )
        res = agent.run(f"{prompt}"
                        "System: get a list for the following query. Translate the titles into spanish"
                        f"Human: {query}")
        return res


    async def _arun(self) -> str:
        raise NotImplementedError("custom_search does not support async")


if __name__ == "__main__":
    finder = FindRecipesByQuery()
    finder._run(query="recipes with Broccoli")
