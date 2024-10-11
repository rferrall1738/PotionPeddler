import sqlalchemy
from src import database as db
from fastapi import APIRouter

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
   
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_green_potions, num_red_potions, num_blue_potions FROM global_inventory"))
        items= result.fetchone()

        num_green_potions= items[0]
        num_red_potions = items[1]
        num_blue_potions = items[2]
       # get rid of the fstring

        print(f"number of potions: Green:{num_green_potions}, Red:{num_red_potions}, Blue:{num_blue_potions}")

        catalog =[]

        if (num_green_potions > 0):
            catalog.append({
                "sku": "GREEN_POTION_0",
                "name": "green potion",
                "quantity": num_green_potions,
                "price": 20,
                "potion_type": [0,100,0,0],

            })
        if (num_red_potions > 0):
            catalog.append({
                "sku": "RED_POTION_0",
                "name": "red potion",
                "quantity": num_red_potions,
                "price": 20,
                "potion_type": [100,0,0,0],

            })   
        if (num_blue_potions > 0):
            catalog.append({
                "sku": "BLUE_POTION_0",
                "name": "blue potion",
                "quantity": num_blue_potions,
                "price": 20,
                "potion_type": [0,0,100,0],

            })                  

            print(catalog)

        return catalog