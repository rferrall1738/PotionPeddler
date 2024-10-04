import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth


router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_bottles(potions_delivered: list[PotionInventory], order_id: int):

    with db.engine.begin() as connection:
        for potion in potions_delivered:
    
            if(potion.potion_type == [1,0,0,0]):
             red = connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = num_red_potions + : quantity WHERE potion_type = [1,0,0,0]"),{
                    "quantity":potion.quantity
                    })
            elif (potion.potion_type == [0,1,0,0]):
             green = connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_potions = num_green_potions + :quantity WHERE potion_type = [0,1,0,0]"),{
                    "quantity": potion.quantity
             })

            elif (potion.potion_type == [0,0,1,0]):
             blue = connection.execute(sqlalchemy.txt("UPDATE global_inventory SET num_blue_potions = num_blue_potions + :quantity WHERE potion_type = [0,0,1,0]"),{
                    "quantity": potion.quantity
             })

    print(f"potions delievered: {potions_delivered} order_id: {order_id}")

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
    potion_ml = 100
    bottler = {}

    potion_types = {
        "green": {"ml_column": "num_green_ml", "potion_column": "num_green_potions", "potion_type": [0, 1, 0, 0]},
        "red": {"ml_column": "num_red_ml", "potion_column": "num_red_potions", "potion_type": [1, 0, 0, 0]},
        "blue": {"ml_column": "num_blue_ml", "potion_column": "num_blue_potions", "potion_type": [0, 0, 1, 0]}
    }

    results = []

    with db.engine.begin() as connection:
        for potion_name, potion_data in potion_types.items():
            bottle_plan = connection.execute(sqlalchemy.text(f"SELECT {potion_data['ml_column']}, {potion_data['potion_column']} FROM global_inventory"))
            inventory = bottle_plan.fetchone()

            if inventory:
                num_potion_ml = inventory[potion_data['ml_column']]

                if num_potion_ml > 0:
    #finds the remaining amount of ml
                    bottler[potion_name] = num_potion_ml // potion_ml
                    bottler_mod = num_potion_ml % potion_ml

                   #place back in db with values
                    connection.execute(sqlalchemy.text(
                        f"UPDATE global_inventory SET {potion_data['potion_column']} = {potion_data['potion_column']} + :bottler, {potion_data['ml_column']} = :bottler_mod"
                    ), {
                        "bottler": bottler[potion_name],
                        "bottler_mod": bottler_mod
                    })

        #show that juicy data
                    results.append({
                        "potion_type": potion_data["potion_type"],
                        "quantity": bottler[potion_name],
                    })

    return results

if __name__ == "__main__":
    print(get_bottle_plan())
