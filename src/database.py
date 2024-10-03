import os
import dotenv
from sqlalchemy import create_engine

def database_connection_url():
    dotenv.load_dotenv()
    POSTGRES_URI= "postgresql://postgres.fdzisynlybwfvbtspgak:pOTIONpAPI720@aws-0-us-west-1.pooler.supabase.com:6543/postgres"
    return os.environ.get(POSTGRES_URI)

engine = create_engine(database_connection_url(), pool_pre_ping=True)

    

