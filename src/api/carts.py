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
        FROM cart_items""")).fetchall()

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
    potential_customers=[]
    with db.engine.begine() as connection:
        visits= connection.execute(sqlalchemy.text("""
    INSERT INTO carts (customer_name, cart_id)
    VALUES(:customer_name, :cart_id)
    RETURNING customer_name                                
    """)).fetchall()
        for visit in visits:
            potential_customers.append(
                {
                    "Customers": visit['customer_name'],
                    "Visit_Id" : visit['cart_id']
                }
            )
    print(customers)

    return potential_customers


@router.post("/")
def create_cart(new_cart: Customer): ## broken
    """ """
    with db.engine.begin() as connection:
        cart_creation = connection.execute(sqlalchemy.text("""
            INSERT INTO carts (customer_name)
            VALUES (:customer_name)
            RETURNING cart_id
        """), {"customer_name": new_cart.customer_name})
        
        cart_id = cart_creation.fetchone()["cart_id"]

        print(cart_creation.customer_name, cart_creation.cart_id)
    
    return {"cart_id": cart_id}

class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}") ###brokenm
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    
    with db.engine.begin() as connection:
        item_quantity = connection.execute(sqlalchemy.text("""
        UPDATE cart_items
        SET quantity = :quantity
        WHERE cart_id = :cart_id AND item_sku = :item_sku
        """)),{
        "quantity": cart_item.quantity, "cart_id" : cart_id, "item_sku" : item_sku
                                                }
        print(item_quantity.quantity, item_quantity.item_sku, item_quantity.cart_id)

    return {"success": True}


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout") ## broken
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """

    with db.engine.begin() as connection:
        checkout = connection.execute(sqlalchemy.text("""
            SELECT sku, red_ml, green_ml, blue_ml, dark_ml, price, quantity
            
            FROM potion_catalog
            INNER JOIN cart_items
                                                      
        """))
        potions = checkout.fetchall()
        
        total_gold_paid = 0
        total_potions_purchased = 0
        
    
        for potion in potions:
            potion_sku = potion.sku
            potion_price = potion.price
            potion_quantity = potion.quantity
            total_gold_paid += potion_quantity * potion_price
            total_potions_purchased += potion_quantity
    
    return {
        "total_potions_bought": total_potions_purchased,
        "total_gold_paid": total_gold_paid
    }