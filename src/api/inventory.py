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
        result= connection.execute(sqlalchemy.text("SELECT (num_green_potions, num_green_ml, gold), FROM global_inventory"))
        inventory = result.fetchone()
    return {"number_of_potions": inventory['num_green_potions'], "ml_in_barrels": inventory['num_green_ml'], "gold": inventory['gold']}

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
        result = connection.execute(sqlalchemy.text("SELECT( num_green_potions,num_green_ml,gold) FROM global_inventory"))
        capacity = result.fetchone()
        if capacity:
            inventory_sum = capacity['num_green_potions']
            ml_sum = capacity['num_green_ml']
            gold = capacity['gold']

            extra_cost_potion_capacity = max(0,math.ceil((inventory_sum -potion_capacity)/ potion_capacity))
            extra_cost_ml_capacity = max(0,math.ceil((ml_sum - ml_capacity)/ ml_capacity ))

            cost_potion_capacity = extra_cost_potion_capacity * capacity_cost
            cost_ml_capacity = extra_cost_ml_capacity * capacity_cost

    return {
        "potion_capacity": potion_capacity + extra_cost_potion_capacity ,
        "ml_capacity": ml_capacity + extra_cost_ml_capacity
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



    
    return "OK"
