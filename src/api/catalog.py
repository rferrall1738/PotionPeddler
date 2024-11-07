import sqlalchemy
from src import database as db
from fastapi import APIRouter

router = APIRouter()


@router.get("/catalog/", tags=["catalog"]) 
def get_catalog():
   
   with db.engine.begin() as connection:
        catalog_description = connection.execute(sqlalchemy.text("""
            SELECT sku,potion_type, quantity, price
            FROM potion_shop
        """))
        potions_catalog = catalog_description.fetchall()

        catalog = []
        
        for potion in potions_catalog:

            catalog.append({
                "sku": potion.sku,
                "name": potion.sku,
                "quantity": potion.quantity,
                "price": potion.price,
                "potion_type": potion.potion_type,  
            })

        return catalog