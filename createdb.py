import sqlite3

conn = sqlite3.connect('qrdb')

print("Database created successfully.")

conn.commit()
