import sqlalchemy
from src import database as db
from fastapi import APIRouter

router = APIRouter()


@router.get("/catalog/", tags=["catalog"]) 
def get_catalog():
   
   with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT sku, red_ml, green_ml, blue_ml, dark_ml, quantity, price
            FROM potion_catalog
        """))
        potions = result.fetchall()

        catalog = []
        
        for potion in potions:
           
            potion_type = [potion.red_ml, potion.green_ml, potion.blue_ml, potion.dark_ml]

            catalog.append({
                "sku": potion.sku,
                "name": potion.sku,
                "quantity": potion.quantity,
                "price": potion.price,
                "potion_type": potion_type,  
            })

        return catalog