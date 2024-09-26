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

        sql_to_execute = """
        UPDATE sql_to_execute
        SET quantity = quantity + :quantity
        WHERE potion_type = :potion_type
        """


        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text(sql_to_execute)),{
            "potion_type": potion_type,
            "quantity": barrel.quantity,
            "volume_per_potion": barrel.ml_per_barrel
            }


    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    return [
        {
            "sku": "SMALL_RED_BARREL",
            "quantity": 1,
        }

        
    ]

