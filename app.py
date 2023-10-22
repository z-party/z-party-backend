from flask import Flask, request,render_template
from db_config import create_async_db_connection
from psycopg2.extras import RealDictCursor
import hashlib
import json

app = Flask(__name__)

# http://127.0.0.1:5000/route?variable1=x&variable2=y

def execute_query(query, response='yes'):
    connection = create_async_db_connection()
    if connection:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(query)
            result = 'No response (is this a POST request?)'
            if response == 'yes':
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


# http://127.0.0.1:5000/account/test/show_events
# test function. maybe in the future route could be /user/show_events (login sesion stored in cache). how do we use guest accounts? 
@app.get("/account/<account_name>/show_events")
def events_by_account(account_name):
    # Get params from the query parameters
    # account_name = request.args.get("account_name")
    
    if account_name is None:
        return {"error": "Account ID or username not provided."}

    # Define the query
    query = f"""
    SELECT e.*
    FROM events e
    INNER JOIN attendance a ON e.event_name = a.event_name
    WHERE a.account_name = '{account_name}';
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

# # http://127.0.0.1:5000/event/shocktober
# @app.route('/event/<event_name>')
# def event(event_name):
    
#     if event_name is None:
#         return {"error": "Event Name not provided."}
    
#     print(event_name)

#     # Define the query
#     query = f"""
#     SELECT *
#     FROM events
#     WHERE event_name = '{event_name}';
#     """

#     # Execute the query
#     return execute_query(query)

@app.route('/event/<event_name>')
def show_form(event_name):
    return render_template('test_form.html', event_name=event_name)

@app.route('/event/<event_name>/submit', methods=['POST'])
def add_attendance(event_name):

    account_name = request.form['account_name']

    TEMPKEY = 'tempkey'
    message = account_name + event_name + TEMPKEY
    m = hashlib.sha256()
    m.update(message.encode('UTF-8'))
    hash = m.hexdigest()

    query = f"""
    INSERT INTO attendance (account_name, event_name, hash, checked_in)
    VALUES ('{account_name}', '{event_name}', '{hash}', false)
    ON CONFLICT (account_name, event_name)
    DO UPDATE SET hash = '{hash}';
    """

    return execute_query(query, response='no')
    
    # return "Form submitted successfully! Thank you, " + account_name
