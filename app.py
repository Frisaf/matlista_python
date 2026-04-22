import asyncio, random
from prisma import Prisma

class Generator:
    def __init__(self, db) -> None:
        self.db = db
    
    def get_random_dish(self, dishes) -> object:
        dish = random.choice(dishes)
        return dish
    
    def find_same(self, dish, dishes) -> list:
        name = dish.name
        result = []

        for dish in dishes:
            if dish.name == name:
                result.append(dish)
        
        return result
    
class Dish:
    def __init__(self, name, main, side, other_info, weekend_worthy) -> None:
        self.name = name
        self.main = main
        self.side = side
        self.other_info = other_info
        self.weekend_worthy = weekend_worthy
    
    def print_info(self, dish):
        return print(f"{dish.name.capitalize()}\nHuvudingrediens: {dish.main}\nTillbehör: {dish.sides}\nÖvrig info: {dish.otherInfo}")

async def main() -> None:
    db = Prisma()
    generator = Generator(db)

    await db.connect()

    dishes = await db.dishes.find_many(
        include = {
            "main": True,
            "side": True
        }
    )
    
    random_dish = generator.get_random_dish(dishes)
    all_dishes = generator.find_same(random_dish, dishes)

    print(dishes)

if __name__ == '__main__':
    asyncio.run(main())