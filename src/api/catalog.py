import sqlalchemy
from src import database as db
from fastapi import APIRouter

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
   
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT (sku,name, quantity,price,potion_type), FROM global_inventory"))
        items= result.fetchall()

        catalog =[]

        for item in items:
            catalog.append({
                "sku": item.sku,
                "name": item.name,
                "quantity": item.quantity,
                "price": item.price,
                "potion_type": item.potion_type,

            })
        return catalog