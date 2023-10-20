from flask import Flask
from db_config import create_async_db_connection
from psycopg2.extras import RealDictCursor
from flask import request

app = Flask(__name__)

# http://127.0.0.1:5000/route?variable1=x&variable2=y

def execute_query(query):
    connection = create_async_db_connection()
    if connection:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            return {"result": result, "connection": "success", "error": "none"}
        except Exception as e:
            return {"error": str(e)}
        finally:
            cursor.close()
            connection.close()
    else:
        return {"connection": "failed"}

@app.route("/")
def hello_world():
    return "connected to db!"

@app.get("/events")
def events():
    query = "SELECT * FROM events;"
    return execute_query(query)

@app.get("/accounts")
def accounts():
    query = "SELECT * FROM accounts;"
    return execute_query(query)

@app.get("/attendance")
def attendance():
    query = "SELECT * FROM attendance;"
    return execute_query(query)

# http://127.0.0.1:5000/events_by_account?account_id=1
@app.get("/events_by_account")
def events_by_account():
    # Get params from the query parameters
    account_id = request.args.get("account_id")
    
    if account_id is None:
        return {"error": "Account ID or username not provided."}

    # Define the query
    query = f"""
    SELECT e.*
    FROM events e
    INNER JOIN attendance a ON e.event_id = a.event_id
    WHERE a.account_id = {account_id};
    """

    # Execute the query
    return execute_query(query)