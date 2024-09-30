import sqlalchemy
from src import database as db
from fastapi import APIRouter

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    execute_sql ="""
    SELECT sku, name, quantity, price, potion_type
    FROM global_inventory
    Each unique item combination must have only a single price.
    """
    with db.engine.begin() as connection:
          result = connection.execute(sqlalchemy.text(execute_sql))

    return [
            {
                "sku": "RED_POTION_0",
                "name": "red potion",
                "quantity": 1,
                "price": 50,
                "potion_type": [100, 0, 0, 0],
            }
        ]
