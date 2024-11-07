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
        result = connection.execute(sqlalchemy.text("""
            SELECT total_potions, total_ml, gold
            FROM inventory_audit
        """))
        inventory = result.fetchone()
    
        return {
        "total_potions": inventory.total_potions,
        "total_ml": inventory.total_ml,
        "gold": inventory.gold
    }


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