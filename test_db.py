from db import get_db_connection

try:
    conn = get_db_connection()
    print("DB connected!")
    conn.close()
except Exception as e:
    print("Error:", e)

