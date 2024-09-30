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

        potion_type = barrel.potion_type[0]




        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text(" UPDATE global_inventory SET num_green_ml = num_green_ml + total_ml WHERE potion_type = :potion_type "),{
            "potion_type": potion_type,
            "total_ml" : total_ml
            }
            )

    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    
    purchase_plan =[]

    with db.engine.begin as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_green_potions, num_green_ml  FROM global_inventory "))
        inventory = result.fetchone()

        if inventory:
            num_green_potions = inventory['num_green_potions']
            num_green_potions = inventory['num_green_ml']

            if num_green_ml > 0:
                potion_mixer = num_green_ml // 100
                mod_potion = num_green_ml % 100

    
                connection.execute(sqlalchemy.text("UPDATE global_inventory  SET num_green_potions = num_green_potions + :potion_mixer,   num_green_ml = : mod_potion WHERE potion_type = 1;"){
                    "potion_mixer": potion_mixer
                    "mod_potion" : mod_potion
                }
                )

    print(wholesale_catalog)

    return [
        {
            "sku": "SMALL_RED_BARREL",
            "quantity": 1,
        }

        
    ]

