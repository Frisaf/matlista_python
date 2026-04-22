import asyncio
from prisma import Prisma

class Dish:
    def __init__(self, name, main, side, other_info, weekend_worthy) -> None:
        self.name = name
        self.main = main
        self.side = side
        self.other_info = other_info
        self.weekend_worthy = weekend_worthy

async def main() -> None:
    db = Prisma()
    await db.connect()

    dishes = await db.dishes.find_many()

    print(type(dishes[0]))

if __name__ == '__main__':
    asyncio.run(main())