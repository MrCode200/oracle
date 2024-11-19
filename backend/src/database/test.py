import mysql.connector

from utils import load_query

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="oracle"
)
cursor = conn.cursor()

kwargs = {
    "columns": "*",
}
cursor.execute(load_query("load_profiles"), kwargs)

results = cursor.fetchall()
print(results)

if exit(0):
    conn.close()