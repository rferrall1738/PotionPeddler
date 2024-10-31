import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum


router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)
class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   

@router.get("/search/", tags=["search"])   ###broken
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc,
):
    """
    Search for cart line items by customer name and/or potion sku.

    Customer name and potion sku filter to orders that contain the 
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.

    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response can be passed in the next search request
    as search page to get that page of results.

    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.

    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku, 
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items.
    """
    items_per_page = 5
    page = []
    with db.engine.begin() as connection:
        carts = connection.execute(sqlalchemy.text("""
        SELECT 
        cart_id, customer_name, item_sku,
        (price * quantity) AS line_item_total,
        timestamp 
        FROM cart_items
        LIMIT 5""")).fetchall()

        for cart in carts :
            page.append( {


                "previous": "",
                "next": "",
                "results": [
            {
                "line_item_id": cart.cart_id,
                "item_sku": cart.item_sku,
                "customer_name": cart.customer_name,
                "line_item_total": cart.line_item_total,
                "timestamp": cart.timestamp,
            }
        ],
            
    }
)   
    return page



class Customer(BaseModel):
    customer_name: str
    character_class: str
    level: int

@router.post("/visits/{visit_id}")
def post_visits(visit_id: int, customers: list[Customer]):
    """
    Log customer visits.
    """
    print(customers)
    return "OK"

@router.post("/")
def create_cart(new_cart: Customer): ## broken
    """ """


    with db.engine.begin() as connection:
        cart_creation = connection.execute(sqlalchemy.text("""
            INSERT INTO carts (customer_name, character_class, level)
            VALUES (:customer_name, :character_class, :level)
            RETURNING cart_id
        """), {"customer_name": new_cart.customer_name,
               "character_class": new_cart.character_class,
               "level": new_cart.level
               })
        result = cart_creation.mappings().fetchone()
        
        cart_id = result['cart_id']

        print(cart_id)
    
    return {"cart_id": cart_id}

class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}") ###broken
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    
    with db.engine.begin() as connection:
        item_quantity = connection.execute(sqlalchemy.text("""
        INSERT INTO cart_items (cart_id, item_sku, quantity)
        VALUES (:cart_id, :item_sku, :quantity)
        RETURNING cart_id, item_sku, quantity
        """),{
         "quantity": cart_item.quantity, 
         "cart_id" : cart_id, 
         "item_sku" : item_sku
         })
        
        result = item_quantity.mappings().fetchone()
        quantity = result['quantity']
        
        print(quantity, item_sku,cart_id)

    return {"success": True}


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout") 
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """

    with db.engine.begin() as connection:
        checkout_cart = connection.execute(sqlalchemy.text("""
            SELECT cart_items.item_sku, cart_items.quantity, potion_catalog.price
            FROM cart_items
            JOIN potion_catalog ON cart_items.item_sku = potion_catalog.sku
            WHERE cart_id = :cart_id
                                                      
        """),{"cart_id": cart_id}).fetchall()
        
        total_cost = sum(potion.quantity *potion.price for potion in checkout_cart)
        potions_bought = len(checkout_cart)
    
        connection.execute(sqlalchemy.text("""
        UPDATE global_inventory
        SET gold = gold + :total_cost
        """), {"total_cost": total_cost}
        )

        connection.execute(sqlalchemy.text("""
        INSERT INTO account_transactions(gold, num_potions,description)
        VALUES (:total_cost, :potions_bought, :description)

"""),{"total_cost":total_cost,
      "potions_bought": potions_bought
      })
    return {
        "total_potions_bought": potions_bought,
        "total_gold_paid": total_cost
    }