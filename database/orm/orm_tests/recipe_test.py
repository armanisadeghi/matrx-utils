# test_orm.py
import asyncio

from common import vcprint
from database.orm.models import CompiledRecipe
from database.state import StateManager


async def test_broker_basic_operations():
    compiled_recipe_id = "aead9f5e-511c-49fb-beaa-f67f45896216"
    version = 7
    recipe_id = "8126ddfe-f7af-4977-a5fa-afc8b77cc03a"

    # vcprint(f"Fetching Compiled Recipe with ID: {compiled_recipe_id}", color="yellow")
    # matching_compiled_recipe = await CompiledRecipe.get(version=version)
    # recipe_dict = matching_compiled_recipe.to_dict()
    # vcprint(recipe_dict, title="Matching Compiled Recipe", color="green", pretty=True)

    # matching_compiled_recipes = await CompiledRecipe.filter(recipe_id=recipe_id).all()
    # recipes_dicts = [r.to_dict() for r in matching_compiled_recipes]
    # vcprint(recipes_dicts, title="Matching Compiled Recipes", color="green", pretty=True)

    # Or if you want to use get() and ensure there's only one with that version
    # highest_version_recipe = await CompiledRecipe.filter(
    #     recipe_id=recipe_id
    # ).order_by('-version').first()
    latest_recipe = await CompiledRecipe.filter(recipe_id=recipe_id).order_by("-version").first()

    print(latest_recipe)
    vcprint(latest_recipe, title="Latest Compiled Recipe", color="green", pretty=True)

    # print(recipe_dict)
    # vcprint(recipe_dict, title="Latest Compiled Recipe", color="blue", pretty=True)

    # vcprint("\nCaching Compiled Recipe:", color="yellow")

    # cached_compiled_recipe = await CompiledRecipe.get(recipe_id=recipe_id)

    # vcprint(cached_compiled_recipe.to_dict(), title="Cached Compiled Recipe", color="green", pretty=True)

    # vcprint("\nFiltering brokers by name='New Broker:", color="yellow")

    # matching_compiled_recipes = await CompiledRecipe.filter(recipe_id=recipe_id).all()

    # vcprint(f"Found {len(matching_compiled_recipes)} matching compiled recipes", color="blue")

    # compiled_recipes_dicts = [b.to_dict() for b in matching_compiled_recipes]

    # vcprint(compiled_recipes_dicts, title="Compiled Recipes", color="green", pretty=True)

    # vcprint("\nFetching related data:", color="yellow")

    # first_compiled_recipe = matching_compiled_recipes[0]

    # await first_broker.fetch_related()

    # print(f"Broker {first_broker.name} relationships loaded.")

    # vcprint(first_broker.to_dict(), title="Broker with Related Data", color="green", pretty=True)

    # vcprint("\nChecking cache policy:", color="yellow")

    # print(f"Broker cache policy: {DataBroker._cache_policy}")

    # in_cache = bool(await StateManager.get(DataBroker, id=broker_id))

    # print(f"Is broker in cache: {in_cache}")

    # vcprint("\nListing all brokers in cache:", color="yellow")

    # cached_brokers = await StateManager.get_all(DataBroker)

    # cached_broker_dicts = [broker.to_dict() for broker in cached_brokers]

    # vcprint(cached_broker_dicts, title="All Cached Brokers", color="green", pretty=True)

    # cache_count = await StateManager.count(DataBroker)

    # vcprint(f"Total brokers in cache: {cache_count}", color="blue")


if __name__ == "__main__":
    asyncio.run(test_broker_basic_operations())
