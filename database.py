import sqlite3

# Database connection
connection = sqlite3.connect("driver_safety.db")

cursor = connection.cursor()

# Create alert history table
cursor.execute("""
CREATE TABLE IF NOT EXISTS alert_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    event TEXT NOT NULL
)
""")

connection.commit()
connection.close()

print("Database created successfully!")