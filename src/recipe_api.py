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


class GetRecipeInfo(BaseTool):
    name = "get_recipe_info"
    description = ("Useful when you need detailed information about a recipe using its ID, including ingredients, "
                   "nutrition, diet, and allergen information.")

    def _run(self, recipe_id: int) -> str:
        api_key = os.environ["SPOONACULAR_API_KEY"]
        base_url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
        params = {
            'apiKey': api_key,
            'includeNutrition': True
        }

        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            return self.format_get_recipe_info_output(response)
        else:
            print("Error:", response.status_code, response.text)
            return ""

    async def _arun(self) -> str:
        raise NotImplementedError("get_recipe_info does not support async")

    @staticmethod
    def format_get_recipe_info_output(response):
        api_dict = response.json()
        # usd / eur - should be automatically updated
        # US / Spain groceries
        recipe_info = dict()
        recipe_info["price_in_spain"] = float(api_dict["pricePerServing"]) * 0.92 * 0.6 / 100
        recipe_info["source_url"] = api_dict["sourceUrl"]
        recipe_info["image_url"] = api_dict["image"]
        recipe_info["instructions"] = api_dict["instructions"]
        recipe_info["title"] = api_dict["title"]
        recipe_info["cooking_minutes"] = api_dict["readyInMinutes"]
        interesting_macros = ["Calories", "Saturated Fat", "Fat", "Carbohydrates",
                              "Sugar", "Cholesterol", "Sodium", "Protein"]
        recipe_info["nutrition"] = [macro for macro in api_dict["nutrition"]["nutrients"] if macro["name"] in interesting_macros]
        return json.dumps(recipe_info, indent=4)


class FindRecipesByIngredients(BaseTool):
    name = "find_recipes_by_ingredients"
    description = ("Useful for when you need find a list of recipes based on ingredients to use and ingredients to not use"
                   "parameters:"
                   "    include_ingredients: comma separated str of ingredients (in english) to use. the ingredients should ALWAYS be translated to english"
                   "    exclude_ingredients: comma separated str of ingredients (in english) to NOT use. the ingredients  should ALWAYS be translated to english")

    def _run(self, include_ingredients: str = "", exclude_ingredients: str = "") -> str:
        base_url = "https://api.spoonacular.com/recipes/complexSearch"
        params = self._get_api_params(include_ingredients, exclude_ingredients)

        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            return self.format_find_recipes_by_ingredients_output(response)
        else:
            print("Error:", response.status_code, response.text)
            return ""

    async def _arun(self) -> str:
        raise NotImplementedError("custom_search does not support async")

    def _get_api_params(self, include_ingredients, exclude_ingredients):
        api_key = os.environ["SPOONACULAR_API_KEY"]
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
        return params

    @staticmethod
    def format_find_recipes_by_ingredients_output(response):
        return json.dumps([{'id': recipe['id'], 'title': recipe['title']} for recipe in response.json()['results']], indent=4)


class FindWeeklyRecipesByIngredients(FindRecipesByIngredients):
    def _get_api_params(self, include_ingredients, exclude_ingredients):
        api_key = os.environ["SPOONACULAR_API_KEY"]
        params = {
            'apiKey': api_key,
            'number': 20,
            'ranking': 1,
            'includeIngredients': include_ingredients,
            'excludeIngredients': exclude_ingredients,
            'ignorePantry': False,
            'sort': 'healthiness',
            'addRecipeInformation': False,
            'addRecipeNutrition': False
        }
        return params


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

        agent = initialize_agent(
            llm=self.get_llm(),
            verbose=DEBUG,
            tools=self._get_tools(),
            agent=AgentType.OPENAI_MULTI_FUNCTIONS
        )
        res = agent.run(f"{prompt}"
                        "System: get a list for the following query. Translate the titles into spanish"
                        f"Human: {query}")
        return res

    def _get_tools(self):
        return [FindRecipesByIngredients()]

    async def _arun(self) -> str:
        raise NotImplementedError("custom_search does not support async")


class FindWeeklyRecipes(FindRecipesByQuery):
    name = "find_weekly_recipes_by_query"
    description = ("Useful for when you need to create a weekly plan of recipes."
                   "Just provide the query of the recipes you want to look for."
                   "Only use this tool when you want to create a weekly plan of recipes")

    def _get_tools(self):
        return [FindWeeklyRecipesByIngredients()]


if __name__ == "__main__":
    finder = FindRecipesByQuery()
    finder._run(query="recipes with Broccoli")
