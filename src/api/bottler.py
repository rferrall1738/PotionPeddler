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
            result = connection.execute(sqlalchemy.text("UPDATE global_inventory SET quantity = quantity +: quantity WHERE potion_type = :potion_type"),{
                    "quantity":potion.quantity,
                    "potion_type":potion.potion_type
                    })
    print(f"potions delievered: {potions_delivered} order_id: {order_id}")

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
    potion_ml = 100
    bottler = 0

    with db.engine.begin() as connection:
        bottle_plan = connection.execute(sqlalchemy.text("SELECT num_green_ml, num_green_potions FROM global_inventory"))
        inventory = bottle_plan.fetchone()

        if inventory:
            num_green_ml = inventory['num_green_ml']

            if num_green_ml > 0:
                bottler = num_green_ml // potion_ml
                bottler_mod = num_green_ml % potion_ml

                result = connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_potions = num_green_potions + :bottler, num_green_ml = :bottler_mod WHERE potion_type = 1"),{
                    "bottler": bottler,
                    "bottler_mod": bottler_mod
                })


    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.


    return [
            {
                "potion_type": [0, 100, 0, 0],
                "quantity": bottler,
            }
        ]

if __name__ == "__main__":
    print(get_bottle_plan())
