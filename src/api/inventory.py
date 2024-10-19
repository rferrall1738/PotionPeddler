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
        result = connection.execute(sqlalchemy.text("SELECT num_green_potions, num_green_ml, num_red_potions, num_red_ml, num_blue_potions, num_blue_ml, num_dark_potions, num_dark_ml, gold FROM global_inventory")).one()

      
        total_potions = [result.num_green_potions+ result.num_red_potions+ result.num_blue_potions + result.num_dark_potions]
        total_ml = [result.num_green_ml + result.num_red_ml + result.num_blue_ml + result.num_dark_ml]
        gold = result.gold


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
   

# Gets called once a day  
@router.post("/deliver/{order_id}")
def deliver_capacity_plan(capacity_purchase : CapacityPurchase, order_id: int):
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """
  
    return "Ok"