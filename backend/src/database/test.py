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
    "profile_name": "test_profile_name"
}
cursor.execute(load_query("load_profile_by_name"), kwargs)

if exit(0):
    conn.close()