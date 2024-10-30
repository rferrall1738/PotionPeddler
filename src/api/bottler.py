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
    
            potion_data = {
                "red": {"ml_column": "num_red_ml", "potion_column": "num_red_potions", "potion_type": [1, 0, 0, 0]},
                "green": {"ml_column": "num_green_ml", "potion_column": "num_green_potions", "potion_type": [0, 1, 0, 0]},
                "blue": {"ml_column": "num_blue_ml", "potion_column": "num_blue_potions", "potion_type": [0, 0, 1, 0]},
                "dark": {"ml_column": "num_dark_ml", "potion_column": "num_dark_potions", "potion_type": [0, 0, 0, 1]}
            }

            for potion_name, data in potion_data.items():
                if potion.potion_type == data["potion_type"]:
                    connection.execute(sqlalchemy.text(f"""
                        UPDATE global_inventory
                        SET {data['potion_column']} = {data['potion_column']} + :quantity
                        WHERE sku = :sku
                    """), {
                        "quantity": potion.quantity,
                        "sku": potion_name.upper() + "_POTION_0"
                    })
    
    print(f"Potions delivered: {potions_delivered}, order_id: {order_id}")
    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
    potion_ml = 100
    results = []

    potion_types = {
        "green": {"ml_column": "num_green_ml", "potion_column": "num_green_potions", "potion_type": [0, 1, 0, 0]},
        "red": {"ml_column": "num_red_ml", "potion_column": "num_red_potions", "potion_type": [1, 0, 0, 0]},
        "blue": {"ml_column": "num_blue_ml", "potion_column": "num_blue_potions", "potion_type": [0, 0, 1, 0]},
        "dark": {"ml_column": "num_dark_ml", "potion_column": "num_dark_potions", "potion_type": [0, 0, 0, 1]}
    }

    

    with db.engine.begin() as connection:
        for potion_name, potion_data in potion_types.items():
            potion_plan = connection.execute(sqlalchemy.text(f"""
                SELECT {potion_data['ml_column']}, {potion_data['potion_column']} 
                FROM global_inventory 
                WHERE id :id 
            """), {"id":5})

            inventory = potion_plan.fetchone()

            if inventory:
                num_potion_ml = inventory[0]

                if num_potion_ml >= potion_ml:
                    num_potions = num_potion_ml // potion_ml
                    remaining_ml = num_potion_ml % potion_ml

                    connection.execute(sqlalchemy.text(f"""
                        UPDATE global_inventory
                        SET {potion_data['potion_column']} = {potion_data['potion_column']} + :num_potions, 
                            {potion_data['ml_column']} = :remaining_ml
                        WHERE id = :id
                    """), {
                        "num_potions": num_potions,
                        "remaining_ml": remaining_ml,
                        "id": 5
                    })

                    results.append({
                        "potion_type": potion_data["potion_type"],
                        "quantity": num_potions,
                    })

    return results

if __name__ == "__main__":
    print(get_bottle_plan())