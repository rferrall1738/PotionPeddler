import sqlalchemy
from src import database as db
from fastapi import APIRouter

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
   
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT sku,name, quantity,price,potion_type FROM potion_catalog"))
        items= result.fetchall()

        catalog =[]

        for item in items:

            potion_types = {

                'green': [0,100,0,0],
                'red': [100,0,0,0],
                'blue':[0,0,100,0]
            }
            catalog.append({
                "sku": item[1],
                "name": item[2],
                "quantity": item[3],
                "price": item[4],
                "potion_type": potion_types.get(item[4]),

            })
        return catalog