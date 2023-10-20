from flask import Flask
from db_config import create_async_db_connection
from psycopg2.extras import RealDictCursor
from flask import request
import hashlib
import json

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


# http://127.0.0.1:5000/events_by_account?account_name=test
# test function
@app.get("/events_by_account")
def events_by_account():
    # Get params from the query parameters
    account_name = request.args.get("account_name")
    
    if account_name is None:
        return {"error": "Account ID or username not provided."}

    # Define the query
    query = f"""
    SELECT e.*
    FROM events e
    INNER JOIN attendance a ON e.event_id = a.event_id
    WHERE a.account_name = {account_name};
    """

    # Execute the query
    return execute_query(query)


# http://127.0.0.1:5000/event/shocktober
@app.route('/event/<event_name>')
def event(event_name):
    
    if event_name is None:
        return {"error": "Event Name not provided."}
    
    print(event_name)

    # Define the query
    query = f"""
    SELECT *
    FROM events
    WHERE event_name = '{event_name}';
    """

    # Execute the query
    return execute_query(query)

@app.get("/account/<account_name>/show_checkin_code")
def show_checkin_code(account_name):

    event_name = request.args.get("event_name")

    if event_name is None:
        return {"error": "event name not provided."}
    
    # Define the query
    query = f"""
    SELECT hash
    FROM attendance
    WHERE event_name = '{event_name}' AND account_name = '{account_name}';
    """

    # Execute the query
    result = execute_query(query)['result'][0]
    hash = result['hash']

    checkin_code = f'http://127.0.0.1:5000/event/{event_name}/checkin?account_name={account_name}&hash={hash}'
    return checkin_code

# def add_attendance():
#     TEMPKEY = 'tempkey'


#     message = account_name + event_name + TEMPKEY
#     m = hashlib.sha256()
#     m.update(message.encode('UTF-8'))
#     hash = m.hexdigest()

#     query = f"""
#         UPDATE attendance
#         SET hash = 'YourSpecifiedValue'
#         WHERE attendance_id = :attendance_id;
#     """