import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)

class Purchase_Capacity(BaseModel):

    potion_capacity:int
    ml_capacity: int



@router.get("/audit")
def get_inventory():

    
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_green_potions, num_green_ml, num_red_potions, num_red_ml, num_blue_potions, num_blue_ml, num_dark_potions, num_dark_ml, gold FROM global_inventory"))
        inventory = result.fetchone()
        num_green_potions = inventory[0]
        num_green_ml = inventory[1]
        num_red_potions = inventory[2]
        num_red_ml = inventory[3]
        num_blue_potions = inventory[4]
        num_blue_ml = inventory[5]
        num_dark_potions = inventory[6]
        num_dark_ml = inventory[7]
        gold = inventory[8]
      
        total_potions = num_green_potions+ num_red_potions+ num_blue_potions + num_dark_potions
        total_ml = num_green_ml + num_red_ml + num_blue_ml + num_dark_ml


    return {"number_of_potions": total_potions, "ml_in_barrels": total_ml, "gold": gold}

# Gets called once a day 
@router.post("/plan")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """

    return {
        "potion_capacity": 50,
        "ml_capacity": 10000
        }


class CapacityPurchase(BaseModel):
    potion_capacity: int
    ml_capacity: int
   

# Gets called once a day  fix this shit
@router.post("/deliver/{order_id}")
def deliver_capacity_plan(capacity_purchase : CapacityPurchase, order_id: int):
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """
    potion_capacity = 50
    ml_capacity = 10000
    capacity_cost = 1000

    total_capacity_potions = capacity_purchase.potion_capacity // potion_capacity  
    total_capacity_ml = capacity_purchase.ml_capacity // ml_capacity

    total_capacity_golds = total_capacity_potions + total_capacity_ml
    total_capacity_cost = total_capacity_golds * capacity_cost

    with db.engine.begin() as connection:
        
        result = connection.execute(sqlalchemy.text(
            """
            UPDATE global_inventory
            SET num_green_potions = num_green_potions + :potion_capacity,
                num_green_ml = num_green_ml + :ml_capacity,
                num_red_potions = num_red_potions + :potion_capacity,
                num_red_ml = num_red_ml + :ml_capacity,
                num_blue_potions = num_blue_potions + :potion_capacity,
                num_blue_ml = num_blue_ml + :ml_capacity,
                num_dark_potions = num_dark_potions + :potion_capacity,
                num_dark_ml = num_dark_ml + :ml_capacity
                gold = gold - :total_capacity_cost
            WHERE gold >= :total_capacity_cost
            RETURNING num_green_potions, num_green_ml, num_red_potions, num_red_ml, 
                      num_blue_potions, num_blue_ml, num_dark_potions,num_dark_ml gold
            """
        ), {
            "potion_capacity": capacity_purchase.potion_capacity,
            "ml_capacity": capacity_purchase.ml_capacity,
            "total_capacity_cost": total_capacity_cost
        })

        inventory = result.fetchone()

        if not inventory:
            return {"ERROR": "Get your gold up."}

    
        num_green_potions, num_green_ml, num_red_potions, num_red_ml, num_blue_potions, num_blue_ml, num_dark_potions, num_dark_ml, gold = inventory

    return {
        "message": "Capacity updated successfully.",
        "order_id": order_id,
        "potion_capacity_added": capacity_purchase.potion_capacity,
        "ml_capacity_added": capacity_purchase.ml_capacity,
        "gold_spent": total_capacity_cost,
        "inventory": {
            "num_green_potions": num_green_potions,
            "num_green_ml": num_green_ml,
            "num_red_potions": num_red_potions,
            "num_red_ml": num_red_ml,
            "num_blue_potions": num_blue_potions,
            "num_blue_ml": num_blue_ml,
            "num_dark_potions": num_dark_potions,
            "num_dark_ml": num_dark_ml,
            "gold": gold
        }
    }