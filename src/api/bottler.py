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
                "red": {"ml_column": "num_red_ml", "potion_column": "num_red_potions", "potion_type": [1, 0, 0, 0],"ml_potion": 50},
                "green": {"ml_column": "num_green_ml", "potion_column": "num_green_potions", "potion_type": [0, 1, 0, 0],"ml_potion": 50},
                "blue": {"ml_column": "num_blue_ml", "potion_column": "num_blue_potions", "potion_type": [0, 0, 1, 0], "ml_potion": 50},
                "dark": {"ml_column": "num_dark_ml", "potion_column": "num_dark_potions", "potion_type": [0, 0, 0, 1], "ml_potion": 50}
            }

            for potion_name, data in potion_data.items():
                if potion.potion_type == data["potion_type"]:
                    connection.execute(sqlalchemy.text(f"""
                        UPDATE global_inventory
                        SET {data['potion_column']} = {data['potion_column']} + :quantity
                        WHERE id = :id
                    """), {
                        "quantity": potion.quantity
                    })

                    connection.execute(sqlalchemy.text(
                        """
                        INSERT INTO account_transactions (num_potions,gold, num_red_ml, num_green_ml, num_blue_ml, num_dark_ml, description)
                        VALUES (:num_potions, -:num_red_ml, -:num_green_ml, -:num_blue_ml,-:num_dark_ml, :description)
                        """ ))
    print(f"Potions delivered: {potions_delivered}, order_id: {order_id}")
    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
    results = []

    potion_types = {
       "green": {"potion_column": "green_potions_possible", "potion_type": [0, 100, 0, 0]},"ml_potion":50,
        "red": {"potion_column": "red_potions_possible", "potion_type": [100, 0, 0, 0],"ml_potion":50},
        "blue": {"potion_column": "blue_potions_possible", "potion_type": [0, 0, 100, 0],"ml_potion":50},
        "dark": {"potion_column": "dark_potions_possible", "potion_type": [0, 0, 0, 100],"ml_potion":50}
    }

    

    with db.engine.begin() as connection:
            potion_inventory = connection.execute(sqlalchemy.text("""
            SELECT id, red_potions_possible, green_potions_possible, blue_potions_possible, dark_potions_possible
            FROM potion_inventory
            WHERE id= :id 
            """), {"id":id}).fetchone()

            if potion_inventory:
                for potion_name, potion_data, in potion_types.items():
                    available_ml = getattr(potion_inventory, potion_data["potion_column"])
                    ml_potion = getattr(potion_inventory, potion_data["potion_column"])

                    num_potions = available_ml//ml_potion

                    if num_potions > 0 :

                        connection.execute(sqlalchemy.text("""
                        INSERT INTO account_transactions (num_potions, description)
                        VALUES (:num_potions, :description)
                        """),{"num_potions":num_potions,
                          "description":"Bottled " + str(num_potions) + " potions of type " + potion_name})

                    results.append({
                        "potion_type": potion_data["potion_type"],
                        "quantity": num_potions,
                    })

    return results

if __name__ == "__main__":
    print(get_bottle_plan())