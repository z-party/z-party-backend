from flask import Flask
from db_config import create_async_db_connection

app = Flask(__name__)

@app.route("/")
def hello_world():
    connection = create_async_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM accounts;")
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        return f"<p>Hello, World! Database Result: {result}</p>"
    return "<p>Hello, World!</p>"

@app.route("/property")
def json():
    connection = create_async_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM property;")
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        return {"Hello,": "World!", "Database Result": result}
    return {"Hello,": "World!"}
