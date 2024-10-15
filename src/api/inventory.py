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
        result = connection.execute(sqlalchemy.text("SELECT num_green_potions, num_green_ml, num_red_potions, num_red_ml, num_blue_potions, num_blue_ml, gold FROM global_inventory"))
        inventory = result.fetchone()
        num_green_potions = inventory[0]
        num_green_ml = inventory[1]
        num_red_potions = inventory[2]
        num_red_ml = inventory[3]
        num_blue_potions = inventory[4]
        num_blue_ml = inventory[5]
        gold = inventory[6]
      
        total_potions = num_green_potions+ num_red_potions+ num_blue_potions
        total_ml = num_green_ml + num_red_ml + num_blue_ml


    return {"number_of_potions": total_potions, "ml_in_barrels": total_ml, "gold": gold}

# Gets called once a day FIX THIS SHIT 
@router.post("/plan")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """
    potion_capacity = 50
    ml_capacity = 10000
    capacity_cost = 1000

   
    
    with db.engine.begin() as connection:
         result = connection.execute(sqlalchemy.text("SELECT num_green_potions, num_green_ml, num_red_potions, num_red_ml, num_blue_potions, num_blue_ml, gold FROM global_inventory" ))
         capacity = result.fetchone()

         if capacity:
            # Green potion inventory
            green_potion_sum = capacity['num_green_potions']or 0 ## render doesn't like this
            green_ml_sum = capacity['num_green_ml'] or 0

      
            red_potion_sum = capacity['num_red_potions'] or 0
            red_ml_sum = capacity['num_red_ml'] or 0 

            blue_potion_sum = capacity['num_blue_potions'] or 0
            blue_ml_sum = capacity['num_blue_ml'] or 0

            gold = capacity['gold'] or 0


            extra_cost_green_potion_capacity = max(0, (green_potion_sum - potion_capacity + potion_capacity - 1) // potion_capacity)
            extra_cost_green_ml_capacity = max(0, (green_ml_sum - ml_capacity + ml_capacity - 1) // ml_capacity)

            extra_cost_red_potion_capacity = max(0, (red_potion_sum - potion_capacity + potion_capacity - 1) // potion_capacity)
            extra_cost_red_ml_capacity = max(0, (red_ml_sum - ml_capacity + ml_capacity - 1) // ml_capacity)

            extra_cost_blue_potion_capacity = max(0, (blue_potion_sum - potion_capacity + potion_capacity - 1) // potion_capacity)
            extra_cost_blue_ml_capacity = max(0, (blue_ml_sum - ml_capacity + ml_capacity - 1) // ml_capacity)

            # Calculate total extra capacities
            total_extra_potion_capacity = extra_cost_green_potion_capacity + extra_cost_red_potion_capacity + extra_cost_blue_potion_capacity
            total_extra_ml_capacity = extra_cost_green_ml_capacity + extra_cost_red_ml_capacity + extra_cost_blue_ml_capacity

            # Calculate total costs
            cost_potion_capacity = total_extra_potion_capacity * capacity_cost
            cost_ml_capacity = total_extra_ml_capacity * capacity_cost


    return {
        "potion_capacity": potion_capacity + total_extra_potion_capacity,
        "ml_capacity": ml_capacity + total_extra_ml_capacity,
        "cost_potion_capacity": cost_potion_capacity,
        "cost_ml_capacity": cost_ml_capacity
    }

##############F\

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
                gold = gold - :total_capacity_cost
            WHERE gold >= :total_capacity_cost
            RETURNING num_green_potions, num_green_ml, num_red_potions, num_red_ml, 
                      num_blue_potions, num_blue_ml, gold
            """
        ), {
            "potion_capacity": capacity_purchase.potion_capacity,
            "ml_capacity": capacity_purchase.ml_capacity,
            "total_capacity_cost": total_capacity_cost
        })

        inventory = result.fetchone()

        if not inventory:
            return {"ERROR": "Get your gold up."}

    
        num_green_potions, num_green_ml, num_red_potions, num_red_ml, num_blue_potions, num_blue_ml, gold = inventory

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
            "gold": gold
        }
    }