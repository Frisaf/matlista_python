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
    
    def get_all_dishes(self, arg) -> list:
        _dish_list = []

        if arg == "all":
            for dish in self.dishes:
                _dish_list.append({"name": dish.name, "side": dish.side.side})
        
        elif arg == "weekend":
            for dish in self.dishes:
                if Dish(dish.name, dish.main.main, dish.side.side, dish.otherInfo, dish.weekendWorthy).is_weekend_worthy():
                    _dish_list.append({"name": dish.name, "side": dish.side.side})
        
        elif arg == "regular":
            for dish in self.dishes:
                if not Dish(dish.name, dish.main.main, dish.side.side, dish.otherInfo, dish.weekendWorthy).is_weekend_worthy():
                    _dish_list.append({"name": dish.name, "side": dish.side.side})

        return _dish_list
    
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
    
    def is_weekend_worthy(self) -> bool:
        if self.weekend_worthy == "YES":
            return True
        
        return False

class DishList(Generator):
    def __init__(self, dishes, db) -> None:
        super().__init__(dishes)
        self.db = db
    
    async def add(self, dish: Dish) -> object:
        name = dish.name
        main = dish.main
        side = dish.sides
        other_info = dish.other_info
        weekend_worthy = dish.weekend_worthy

        same = self.find_same(dish)
        same_sides = self.get_sides(same)
        is_duplicate = True if side in same_sides else False

        if is_duplicate:
            print("Den här rätten finns redan")
            return False
        
        main_id = await self.db.main.find_first(
            where = {
                "main": main
            }
        )
        side_id = await self.db.side.find_first(
            where = {
                "side": side
            }
        )

        if not main_id:
            main_id = await self.db.main.create(
                data = {
                    "main": main
                }
            )
        
        if not side_id:
            side_id = await self.db.side.create(
                data = {
                    "side": side
                }
            )

        return await self.db.dishes.create(
            data = {
                "name": name,
                "mainId": main_id.id,
                "sideId": side_id.id,
                "otherInfo": other_info,
                "weekendWorthy": weekend_worthy
            }
        )
    
    def seek(self, arg) -> list:
        result = [x for x in self.dishes if x.name == arg]
        print(result)

        print("Sökresultat:")

        for i in range(len(result)):
            print(f"[{i + 1}] {result[i].name} ({result[i].side.side})")
        
        return result
    
    async def destroy(self, arg: str) -> object: # yes this is a Metallica reference :p
        result = self.seek(arg)

        while True:
            try:
                choice = int(input("Vilken av dem vill du ta bort?\n> "))
                dish_to_remove = result[choice - 1]
                break
            
            except ValueError:
                print("Vänligen ange in en giltig siffra.")
            
        await self.db.dishes.delete(
            where = {
                "id": dish_to_remove.id
            }
        )

        return dish_to_remove

    def print_dish_list(self, arg: str) -> None:
        if arg == "all":
            print("ALLA MATRÄTTER")
        
        elif arg == "weekend":
            print("ALL HELGMAT")
        
        elif arg == "regular":
            print("ALL VARDAGSMAT")

        all_dishes = self.get_all_dishes(arg) # type: ignore
        
        for dish in all_dishes:
            print(f"{dish['name']} ({dish['side']})")

async def main() -> None:
    db = Prisma()

    await db.connect()

    while True:
        dishes = await db.dishes.find_many(
            include = {
                "main": True,
                "side": True
            }
        )
        generator = Generator(dishes)
        dish_list = DishList(dishes, db)
        choices = "1. Nytt matförslag\n2. Visa alla maträtter\n3. Visa alla helgrätter\n4. Visa all vardagsmat\n5. Lägg till maträtt\n6. Sök och ta bort maträtt"

        print("ALTERNATIV\n" + choices)

        choice = input("Vad vill du göra?\n> ")

        if choice == "1":
            generator.compile_dish().print_info() # type: ignore
        
        elif choice == "2":
            dish_list.print_dish_list("all")
        
        elif choice == "3":
            dish_list.print_dish_list("weekend")
        
        elif choice == "4":
            dish_list.print_dish_list("regular")
        
        elif choice == "5":
            name = input("Maträttens namn:\n> ").capitalize()
            main = input("Rättens huvudingrediens:\n> ").capitalize()
            side = input("Rättens tillbehör:\n> ").capitalize()
            other_info = input("Övrig info om rätten (lämna tom om det inte finns någon):\n> ")
            
            while True:
                weekend_worthy = input("Är rätten helgvärdig? [y/n]:\n> ").lower()

                if weekend_worthy in ["y", "n"]:
                    weekend_worthy = "YES" if weekend_worthy == "y" else "NO"
                    break

            new_dish = await dish_list.add(Dish(name, main, side, other_info, weekend_worthy))

            if new_dish:
                print(f"Lade till {new_dish.name} till matlistan.") # type: ignore
        
        elif choice == "6":
            removed = await dish_list.destroy(input("Sök efter maträtter att ta bort. Sök efter maträttens namn\n> "))
            print(f"Tog bort {removed.name} från matlistan") # type: ignore
        
        else:
            print("Vänligen fyll i ett giltigt alternativ.")

if __name__ == '__main__':
    asyncio.run(main())