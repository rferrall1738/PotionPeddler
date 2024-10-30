import sqlalchemy
from src import database as db
from fastapi import APIRouter

router = APIRouter()


@router.get("/catalog/", tags=["catalog"]) 
def get_catalog():
   
   with db.engine.begin() as connection:
        catalog_description = connection.execute(sqlalchemy.text("""
            SELECT sku, amount_red, amount_green, amount_blue, amount_dark, quantity, price
            FROM potion_catalog
        """))
        potions_catalog = catalog_description.fetchall()

        catalog = []
        
        for potion in potions_catalog:
           
            potion_type = potion.amount_red, potion.amount_green, potion.amount_blue, potion.amount_dark

            catalog.append({
                "sku": potion.sku,
                "name": potion.sku,
                "quantity": potion.quantity,
                "price": potion.price,
                "potion_type": potion_type,  
            })

        return catalog