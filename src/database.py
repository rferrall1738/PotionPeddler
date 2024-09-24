import os
import dotenv
from sqlalchemy import create_engine

def database_connection_url():
    dotenv.load_dotenv()

    return os.environ.get("POSTGRES_URI")

engine = create_engine(database_connection_url(), pool_pre_ping=True)

with engine.begin() as connection:
    connection.execute(sqlalchemy.text(" INSERT INTO global_inventory (num_green_potions, num_green_ml, gold) VALUES ('0', '0', '100' ))

    result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
    for row in result:
        print(row)
    connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_potions = '300'))
    

