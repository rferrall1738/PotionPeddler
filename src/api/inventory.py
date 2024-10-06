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
        green_potions, green_ml= connection.execute(sqlalchemy.text("SELECT num_green_potions, num_green_ml FROM global_inventory")).fetchone()

        red_potions,red_ml = connection.execute(sqlalchemy.text("SELECT num_red_potions, num_red_ml FROM global_inventory")).fetchone()

        blue_potions,blue_ml = connection.execute(sqlalchemy.text("SELECT num_blue_potions,num_blue_ml FROM global_inventory")).fetchone()
        
        gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory")).fetchone()
       
     
        total_potions = green_potions, red_potions, blue_potions
        total_ml = green_ml + red_ml + blue_ml


    return {"number_of_potions": total_potions, "ml_in_barrels": total_ml, "gold": gold}

# Gets called once a day
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
            green_potion_sum = capacity['num_green_potions']
            green_ml_sum = capacity['num_green_ml']

      
            red_potion_sum = capacity['num_red_potions']
            red_ml_sum = capacity['num_red_ml']

            blue_potion_sum = capacity['num_blue_potions']
            blue_ml_sum = capacity['num_blue_ml']

            gold = capacity['gold']

            # Calculate extra capacity 
            extra_cost_green_potion_capacity = max(0, math.ceil((green_potion_sum - potion_capacity) / potion_capacity))
            extra_cost_green_ml_capacity = max(0, math.ceil((green_ml_sum - ml_capacity) / ml_capacity))

            extra_cost_red_potion_capacity = max(0, math.ceil((red_potion_sum - potion_capacity) / potion_capacity))
            extra_cost_red_ml_capacity = max(0, math.ceil((red_ml_sum - ml_capacity) / ml_capacity))

            extra_cost_blue_potion_capacity = max(0, math.ceil((blue_potion_sum - potion_capacity) / potion_capacity))
            extra_cost_blue_ml_capacity = max(0, math.ceil((blue_ml_sum - ml_capacity) / ml_capacity))

            # Calculate total costs
            total_extra_potion_capacity = extra_cost_green_potion_capacity + extra_cost_red_potion_capacity + extra_cost_blue_potion_capacity
            total_extra_ml_capacity = extra_cost_green_ml_capacity + extra_cost_red_ml_capacity + extra_cost_blue_ml_capacity

            cost_potion_capacity = total_extra_potion_capacity * capacity_cost
            cost_ml_capacity = total_extra_ml_capacity * capacity_cost

    return {
        "potion_capacity": potion_capacity + total_extra_potion_capacity,
        "ml_capacity": ml_capacity + total_extra_ml_capacity,
        "cost_potion_capacity": cost_potion_capacity,
        "cost_ml_capacity": cost_ml_capacity
    }

class CapacityPurchase(BaseModel):
    potion_capacity: int
    ml_capacity: int
   

# Gets called once a day
@router.post("/deliver/{order_id}")
def deliver_capacity_plan(capacity_purchase : CapacityPurchase, order_id: int):
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """
    potion_capacity = 50
    ml_capacity = 10000
    capacity_cost = 1000

    with db.engine.begin() as connection:
        
        result = connection.execute(sqlalchemy.text( "SELECT num_green_potions, num_green_ml, num_red_potions, num_red_ml, num_blue_potions, num_blue_ml, gold FROM global_inventory" ))
        inventory = result.fetchone()

        if not inventory:
            return {"doesn't exist here"}

        current_gold = inventory['gold']

        total_capacity_golds = capacity_purchase.potion_capacity + (capacity_purchase.ml_capacity // ml_capacity)
        total_capacity_cost = total_capacity_golds * capacity_cost

    
        if total_capacity_cost > current_gold:
            return {"ERROR": "Too broke for more capacity."}

    
        connection.execute(sqlalchemy.text(
            "UPDATE global_inventory SET num_green_potions = num_green_potions + :potion_capacity, num_green_ml = num_green_ml + :ml_capacity, "
            "num_red_potions = num_red_potions + :potion_capacity, "
            "num_red_ml = num_red_ml + :ml_capacity, "
            "num_blue_potions = num_blue_potions + :potion_capacity, "
            "num_blue_ml = num_blue_ml + :ml_capacity, "
            "gold = gold - :total_capacity_cost"
        ), {
            "potion_capacity": capacity_purchase.potion_capacity,
            "ml_capacity": capacity_purchase.ml_capacity,
            "total_capacity_cost": total_capacity_cost
        })

    return {
        "message": "Capacity updated successfully.",
        "order_id": order_id,
        "potion_capacity_added": capacity_purchase.potion_capacity,
        "ml_capacity_added": capacity_purchase.ml_capacity,
        "gold_spent": total_capacity_cost
    }