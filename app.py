import asyncio, random
from prisma import Prisma

class Generator:
    def __init__(self, dishes) -> None:
        self.dishes = dishes # table with all dishes from the db
    
    def get_random_dish(self) -> object:
        dish = random.choice(self.dishes)
        return dish
    
    def find_same(self, dish: object) -> list:
        name = dish.name # type: ignore
        result = []

        for item in self.dishes:
            if item.name == name:
                result.append(item)
        
        return result
    
    def get_sides(self, dish_versions: list) -> list:
        sides = []

        for item in dish_versions:
            sides.append(item.side.side)
        
        return sides
    
    def get_main(self, dish_list: list) -> str:
        main = dish_list[0].main.main
        
        return main
    
    def get_other_info(self, dish_list: list) -> set:
        other_info = [x.otherInfo for x in dish_list]
        other_info_filtered = set(other_info)

        return other_info_filtered
    
    def compile_dish(self) -> object:
        random_dish = self.get_random_dish()
        same_dishes = self.find_same(random_dish)
        sides = self.get_sides(same_dishes)
        main = self.get_main(same_dishes)
        other_info = self.get_other_info(same_dishes)
        dish = Dish(same_dishes[0].name, main, ", ".join(x for x in sides), ", ".join(x for x in other_info), same_dishes[0].weekendWorthy)
        
        return dish
    
class Dish:
    def __init__(self, name, main, sides, other_info, weekend_worthy) -> None:
        self.name = name
        self.main = main
        self.sides = sides
        self.other_info = other_info
        self.weekend_worthy = weekend_worthy
    
    def print_info(self) -> None:
        print(f"Ska vi äta... {self.name.upper()}")
        print(f"Huvudingrediens: {self.main}")

        if self.sides != "":
            print(f"Tillbehör: {self.sides}")
        
        if self.other_info != "":
            print(f"Övrig info: {self.other_info}")
        
        print(f"Helgvärdig: {self.weekend_worthy}")

async def main() -> None:
    db = Prisma()

    await db.connect()

    dishes = await db.dishes.find_many(
        include = {
            "main": True,
            "side": True
        }
    )
    generator = Generator(dishes)

    while True:
        choices = "1. Nytt matförslag"

        print("ALTERNATIV\n", choices)

        choice = input("Vad vill du göra?\n> ")

        if choice == "1":
            generator.compile_dish().print_info() # type: ignore
        
        else:
            print("Vänligen fyll i ett giltigt alternativ.")

if __name__ == '__main__':
    asyncio.run(main())