import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    """ """
    for barrel in barrels_delivered:
        total_ml = barrel.ml_per_barrel * barrel.quantity

  
        if barrel.potion_type == [0,1,0,0]:
            with db.engine.begin() as connection:
                connection.execute(sqlalchemy.text(""" 
            UPDATE global_inventory 
            SET num_green_ml = num_green_ml + :total_ml"""),{
             "total_ml" : total_ml
            }
            )
        elif barrel.potion_type ==[1,0,0,0]:
            with db.engine.begin() as connection:
                connection.execute(sqlalchemy.text("""
            UPDATE global_inventory 
            SET num_red_ml = num_red_ml + :total_ml"""),{
                "total_ml" : total_ml
                })
        elif barrel.potion_type == [0,0,1,0]:
            with db.engine.begin() as connection:
                connection.execute(sqlalchemy.text("""
                UPDATE global_inventory 
                SET num_blue_ml = num_blue_ml + :total_ml"""),{
                    "total_ml": total_ml
                }
                )
        elif barrel.potion_type == [0,0,0,1]:
            with db.engine.begin() as connection:
                connection.execute(sqlalchemy.text("""
                UPDATE global_inventory 
                SET num_dark_ml = num_dark_ml + :total_ml"""),{
                    "total_ml": total_ml
                }   
    )
                connection.execute(sqlalchemy.text("""
                INSERT INTO account_transactions(num_red_ml, num_green_ml, num_blue_ml, num_dark_ml, gold, description)
                VALUES (-:gold, :num_red_ml, :num_blue_ml, :num_green_ml, :num_dark_ml, :description)
                """))
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    return "OK"

# Gets called once a day
@router.post("/plan") 
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    
  with db.engine.begin() as connection:
    result = connection.execute(sqlalchemy.text("""
            SELECT num_green_potions, num_red_potions, num_blue_potions, gold 
            FROM global_inventory
        """))
    inventory = result.fetchone()

    num_green_potions = inventory[0]
    num_red_potions = inventory[1]
    num_blue_potions = inventory[2]
    gold = inventory[3]

    purchase_plan = []

    # green one first 
    if num_green_potions < 10:
        if gold >= 400:
            purchase_plan.append({"sku": "LARGE_GREEN_BARREL", "quantity": 1})
            gold -= 400
        elif gold >= 250:
            purchase_plan.append({"sku": "MEDIUM_GREEN_BARREL", "quantity": 1})
            gold -= 250
        elif gold >= 100:
            purchase_plan.append({"sku": "SMALL_GREEN_BARREL", "quantity": 1})
            gold -= 100
        elif gold >= 60:
            purchase_plan.append({"sku": "MINI_GREEN_BARREL", "quantity": 1})
            gold -= 60

    # i like blue more than red
    if num_blue_potions < 10 and gold > 0:
        if gold >= 600:
            purchase_plan.append({"sku": "LARGE_BLUE_BARREL", "quantity": 1})
            gold -= 600
        elif gold >= 300:
            purchase_plan.append({"sku": "MEDIUM_BLUE_BARREL", "quantity": 1})
            gold -= 300
        elif gold >= 120:
            purchase_plan.append({"sku": "SMALL_BLUE_BARREL", "quantity": 1})
            gold -= 120
        elif gold >= 60:
            purchase_plan.append({"sku": "MINI_BLUE_BARREL", "quantity": 1})
            gold -= 60

    # last resort
    if num_red_potions < 10 and gold > 0:
        if gold >= 500:
            purchase_plan.append({"sku": "LARGE_RED_BARREL", "quantity": 1})
            gold -= 500
        elif gold >= 250:
            purchase_plan.append({"sku": "MEDIUM_RED_BARREL", "quantity": 1})
            gold -= 250
        elif gold >= 100:
            purchase_plan.append({"sku": "SMALL_RED_BARREL", "quantity": 1})
            gold -= 100
        elif gold >= 60:
            purchase_plan.append({"sku": "MINI_RED_BARREL", "quantity": 1})
            gold -= 60

   


    return purchase_plan