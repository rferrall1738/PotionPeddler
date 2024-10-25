import sqlalchemy
from src import database as db
from fastapi import APIRouter

router = APIRouter()


@router.get("/catalog/", tags=["catalog"]) 
def get_catalog():
   
   with db.engine.begin() as connection:
        catalog_description = connection.execute(sqlalchemy.text("""
            SELECT sku, num_red_ml, num_green_ml, num_blue_ml, num_dark_ml, quantity, price
            FROM potion_catalog
        """))
        potions_catalog = catalog_description.fetchall()

        catalog = []
        
        for potion in potions_catalog:
           
            potion_type = potion.num_red_ml, potion.num_green_ml, potion.num_blue_ml, potion.num_dark_ml

            catalog.append({
                "sku": potion.sku,
                "name": potion.sku,
                "quantity": potion.quantity,
                "price": potion.price,
                "potion_type": potion_type,  
            })

        return catalog