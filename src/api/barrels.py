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
             result = connection.execute(sqlalchemy.text(" UPDATE global_inventory SET num_green_ml = num_green_ml + total_ml: total_ml "),{
             "total_ml" : total_ml
            }
            )
        elif barrel.potion_type ==[1,0,0,0]:
            with db.engine.begin() as connection:
                result = connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = num_red_ml + total_ml: total_ml ")),{
                "total_ml" : total_ml
                }
        elif barrel.potion_type == [0,0,1,0]:
            with db.engine.begin() as connection:
                result = connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_ml = num_blue_ml + total_ml: total_ml")),{
                    "total_ml": total_ml
                }
        
    
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    
    purchase_plan =[]

    barrels = {"MINI_GREEN_BARREL": {"ml_per_barrel": 200,"price":60},
               "SMALL_GREEN_BARREL":{"ml_per_barrel": 500,"price":100},
               "MEDIUM_GREEN_BARREL":{"ml_per_barrel": 2500,"price":250},

               "MEDIUM_RED_BARREL":{"ml_per_barrel": 2500,"price":250},
               "MINI_RED_BARREL": {"ml_per_barrel": 200,"price":60},
               "SMALL_RED_BARREL":{"ml_per_barrel": 500,"price":100},
               
               "MEDIUM_BLUE_BARREL":{"ml_per_barrel": 2500,"price":250},
               "MINI_BLUE_BARREL": {"ml_per_barrel": 200,"price":60},
               "SMALL_BLUE_BARREL":{"ml_per_barrel": 500,"price":120},

               }
    
#looks at what i got in the inventory
    with db.engine.begin as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_green_potions, num_green_ml, num_red_potions, num_red_ml, num_blue_potions, num_blue_ml, gold FROM global_inventory"))
        inventory = result.fetchone()

        if inventory:
            num_green_potions = inventory['num_green_potions']
            num_green_ml = inventory['num_green_ml']
            num_red_potions = inventory['num_red_potions']
            num_red_ml = inventory['num_red_ml']
            num_blue_potions = inventory['num_blue_potions']
            num_blue_ml = inventory['num_blue_ml']
            gold = inventory['gold']

            if num_green_potions < 10:
                if gold >= barrels["SMALL_GREEN_BARREL"]["price"]:

                    purchase_plan.append({
                    "sku": "SMALL_GREEN_BARREL",
                    "quantity": 1,
                    "ml_per_barrel": barrels["SMALL_GREEN_BARREL"]["ml_per_barrel"],
                    "price": barrels["SMALL_GREEN_BARREL"]["price"]})

                    connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = gold - :barrel_price, num_green_ml = num_green_ml + :ml_per_barrel"),
                        {
                        "barrel_price": barrels["SMALL_GREEN_BARREL"]["price"],
                        "ml_per_barrel": barrels["SMALL_GREEN_BARREL"]["price"]
                    })
                    
                
                elif gold >= barrels["MINI_GREEN_BARREL"]["price"]:

                    purchase_plan.append({
                        "sku": "MINI_GREEN_BARREL",
                        "quantity": 1,
                        "ml_per_barrel": barrels["MINI_GREEN_BARREL"]["ml_per_barrel"],
                        "price": barrels["MINI_GREEN_BARREL"]["price"]})

                    connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = gold - :barrel_price, num_green_ml = num_green_ml + : ml_per_barrel"),
                        {
                        "barrel_price" : barrels["MINI_GREEN_BARREL"]["price"],
                        "ml_per_barrel" : barrels["MINI_GREEN_BARREL"]["ml_per_barrel"]
                        })
                if num_red_potions < 10:
                    if gold >= barrels["SMALL_RED_BARREL"]["price"]:

                        purchase_plan.append({ "sku": "SMALL_RED_BARREL",
                        "quantity": 1,
                        "ml_per_barrel": barrels["SMALL_RED_BARREL"]["ml_per_barrel"],
                        "price": barrels["SMALL_RED_BARREL"]["price"]
                    })
                    connection.execute(sqlalchemy.text(
                        "UPDATE global_inventory SET gold = gold - :barrel_price, num_red_ml = num_red_ml + :ml_per_barrel"),
                        {"barrel_price": barrels["SMALL_RED_BARREL"]["price"], "ml_per_barrel": barrels["SMALL_RED_BARREL"]["ml_per_barrel"]}
                    )
                elif gold >= barrels["MINI_RED_BARREL"]["price"]:
                    purchase_plan.append({
                        "sku": "MINI_RED_BARREL",
                        "quantity": 1,
                        "ml_per_barrel": barrels["MINI_RED_BARREL"]["ml_per_barrel"],
                        "price": barrels["MINI_RED_BARREL"]["price"]
                    })
                    connection.execute(sqlalchemy.text(
                        "UPDATE global_inventory SET gold = gold - :barrel_price, num_red_ml = num_red_ml + :ml_per_barrel"),
                        {"barrel_price": barrels["MINI_RED_BARREL"]["price"], "ml_per_barrel": barrels["MINI_RED_BARREL"]["ml_per_barrel"]}
                    )

            if num_blue_potions < 10:
                if gold >= barrels["SMALL_BLUE_BARREL"]["price"]:
                    purchase_plan.append({
                        "sku": "SMALL_BLUE_BARREL",
                        "quantity": 1,
                        "ml_per_barrel": barrels["SMALL_BLUE_BARREL"]["ml_per_barrel"],
                        "price": barrels["SMALL_BLUE_BARREL"]["price"]
                    })
                    connection.execute(sqlalchemy.text(
                        "UPDATE global_inventory SET gold = gold - :barrel_price, num_blue_ml = num_blue_ml + :ml_per_barrel"),
                        {"barrel_price": barrels["SMALL_BLUE_BARREL"]["price"], "ml_per_barrel": barrels["SMALL_BLUE_BARREL"]["ml_per_barrel"]}
                    )
                elif gold >= barrels["MINI_BLUE_BARREL"]["price"]:
                    purchase_plan.append({
                        "sku": "MINI_BLUE_BARREL",
                        "quantity": 1,
                        "ml_per_barrel": barrels["MINI_BLUE_BARREL"]["ml_per_barrel"],
                        "price": barrels["MINI_BLUE_BARREL"]["price"]
                    })
                    connection.execute(sqlalchemy.text(
                        "UPDATE global_inventory SET gold = gold - :barrel_price, num_blue_ml = num_blue_ml + :ml_per_barrel"),
                        {"barrel_price": barrels["MINI_BLUE_BARREL"]["price"], "ml_per_barrel": barrels["MINI_BLUE_BARREL"]["ml_per_barrel"]}
                    )

            if num_green_ml > 0:
                potion_mixer = num_green_ml // 100
                mod_potion = num_green_ml % 100
                connection.execute(sqlalchemy.text(
                    "UPDATE global_inventory SET num_green_potions = num_green_potions + :potion_mixer, num_green_ml = :mod_potion"),
                    {"potion_mixer": potion_mixer, "mod_potion": mod_potion}
                )

            if num_red_ml > 0:
                potion_mixer = num_red_ml // 100
                mod_potion = num_red_ml % 100
                connection.execute(sqlalchemy.text(
                    "UPDATE global_inventory SET num_red_potions = num_red_potions + :potion_mixer, num_red_ml = :mod_potion"),
                    {"potion_mixer": potion_mixer, "mod_potion": mod_potion}
                )

            if num_blue_ml > 0:
                potion_mixer = num_blue_ml // 100
                mod_potion = num_blue_ml % 100
                connection.execute(sqlalchemy.text(
                    "UPDATE global_inventory SET num_blue_potions = num_blue_potions + :potion_mixer, num_blue_ml = :mod_potion"),
                    {"potion_mixer": potion_mixer, "mod_potion": mod_potion}
                )
    return purchase_plan