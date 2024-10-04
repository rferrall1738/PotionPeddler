import sqlalchemy
from src import database as db
from fastapi import APIRouter

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
   
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT sku,name, quantity,price,potion_type FROM global_inventory"))
        items= result.fetchall()

        catalog =[]

        for item in items:

            potion_types = {

                'green': [0,1,0,0],
                'red': [1,0,0,0],
                'blue':[0,0,1,0]
            }
            catalog.append({
                "sku": item.sku,
                "name": item.name,
                "quantity": item.quantity,
                "price": item.price,
                "potion_type": potion_types.get(item.potion_type),

            })
        return catalog