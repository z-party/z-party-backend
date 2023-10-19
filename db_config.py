import psycopg2
import asyncio

def create_async_db_connection():
    # database configuration
    db_params = {
        'host'     : 'dev-database.cfa8nnooilud.us-east-2.rds.amazonaws.com',
        'user'     : 'postgres',
        'password' : 'devpass09222023',
        'port'     : 5432,
        'database' : "real-mgmt"
    }


    conn = psycopg2.connect(**db_params)
    conn.autocommit = True
    return conn
