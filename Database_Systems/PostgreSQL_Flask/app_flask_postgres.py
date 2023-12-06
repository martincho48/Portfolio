#https://blog.teclado.com/first-rest-api-flask-postgresql-python/


import os
import psycopg2 #PosgreSQL adapter for Python
from dotenv import load_dotenv #loads .env file = connects with the database

from flask import Flask, request

#create a table 'rooms' if it doesn't exist with 2 columns 
CREATE_ROOMS_TABLE=(
    """CREATE TABLE IF NOT EXISTS rooms (
        id SERIAL PRIMARY KEY, 
        name TEXT
    );"""
)


#create a table 'temperatures' link it with 'rooms' table
#secure that if a record in 'rooms' table is deleted then the 'temperaures' record is deleted as well 
CREATE_TEMPS_TABLE=(
    """CREATE TABLE IF NOT EXISTS temperatures (
        room_id INTEGER, 
        temperature REAL,
        date TIMESTAMP,
        FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE CASCADE
    );"""
)

INSERT_ROOM_RETURN_ID="INSERT INTO rooms(name) VALUES (%s) RETURNING id;"

INSERT_TEMP="INSERT INTO temperatures(room_id, temperature, date) VALUES (%s, %s, %s);"



load_dotenv()

app=Flask(__name__)


url=os.getenv("DATABASE_URL")
connection=psycopg2.connect(url)


@app.post("/api/room")
def create_room():

    #input from the customer in JSON format
    data = request.get_json()
    name = data["name"]

    #connect to the database and activate SQL queries
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_ROOMS_TABLE)
            cursor.execute(INSERT_ROOM_RETURN_ID, (name,))
            room_id = cursor.fetchone()[0]
    return {"id": room_id, "message": f"Room {name} created."}, 201

if __name__ == "__main__":
    app.run(debug=True)





