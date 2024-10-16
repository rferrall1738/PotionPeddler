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

@router.get("/search/", tags=["search"])
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

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT customer_name, item_sku,(price * quantity) AS line_item_total,timestamp FROM cart_items"))

    return {
        "previous": "",
        "next": "",
        "results": [
            {
                "line_item_id": 1,
                "item_sku": "1 oblivion potion",
                "customer_name": "Scaramouche",
                "line_item_total": 50,
                "timestamp": "2021-01-01T00:00:00Z",
            }
        ],
    }


class Customer(BaseModel):
    customer_name: str
    character_class: str
    level: int

@router.post("/visits/{visit_id}")
def post_visits(visit_id: int, customers: list[Customer]):
    """
    Which customers visited the shop today?
    """
    print(customers)

    return "OK"


@router.post("/")
def create_cart(new_cart: Customer):
    """ """
    global cart_dict
    return {"cart_id": 1}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""
        UPDATE cart_items
        SET quantity = :quantity
        WHERE cart_id = :cart_id AND item_sku = :item_sku
                                                """)),{
        "quantity": cart_item.quantity, "cart_id" : cart_id, "item_sku" : item_sku
                                                }

    return {"success": True}


class CartCheckout(BaseModel):
    payment: str
# fix it 
@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """


    with db.engine.begin() as connection:
        # Select the total cost for each potion type in the cart
        result = connection.execute(sqlalchemy.text("""
            SELECT num_green_potions, num_blue_potions,num_red_potions, num_dark_potions
            FROM global_inventory
        """))
        potions = result.fetchone()

        num_red_potion = potions[0]
        num_green_potion = potions[1]
        num_blue_potion = potions[2]
        num_dark_potions = potions[3]

    
    
        inventory ={
            "green_potion": result['num_green_potions'],
             "red_potion": result['num_red_potions'],
              "blue_potion": result['num_blue_potions'],
        }

       
        potion_price = {
            "green_potion": 10,
            "red_potion": 20,
            "blue_potion":30,
            "dark_potion":8
        }

        total_potions_purchased = 0
        total_gold_paid = 0

        gold_green = num_green_potion * potion_price
        gold_red = num_red_potion * potion_price
        gold_blue = num_blue_potion * potion_price
        gold_dark = num_dark_potions * potion_price
        total_gold_paid = gold_green + gold_blue + gold_red

     
       

        total_gold_paid = gold_green + gold_blue + gold_red + gold_dark
        total_potions_purchased = num_green_potion + num_red_potion + num_blue_potion + num_dark_potions

    return {
        "total_potions_bought": total_potions_purchased,
        "total_gold_paid": total_gold_paid
    }