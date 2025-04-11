from common import vcprint
from database.orm.models import CompiledRecipeManager
import asyncio


async def compiled_recipe_manager_test(compiled_recipe_id):
    compiled_recipe_manager = CompiledRecipeManager()

    compiled_recipe = await compiled_recipe_manager.load_item(id=compiled_recipe_id)
    print(compiled_recipe.runtime.dto.to_dict())
    vcprint(
        compiled_recipe,
        "Compiled Recipe Data",
        verbose=True,
        pretty=True,
        color="bright_lavender",
    )

    return compiled_recipe, compiled_recipe_manager


class FunctionMaker:
    def __init__(self):
        pass


async def function_test(func_id):
    function_maker = FunctionMaker()
    my_function = await function_maker.load_item(id=func_id)
    my_function.module_path = "new_module_path"
    data = function_maker.get_item_attributes(my_function)
    vcprint(data, color="green", pretty=True)


if __name__ == "__main__":
    import asyncio

    asyncio.run(compiled_recipe_manager_test("2792145c-d6af-41d8-9e02-3116a1099e7f"))
