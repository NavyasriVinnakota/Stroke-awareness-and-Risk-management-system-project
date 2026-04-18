import sqlite3

# Database create/connect
conn = sqlite3.connect('users.db')

# Cursor create
cur = conn.cursor()

# Table create
cur.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    password TEXT
)
''')
cur.execute('''
CREATE TABLE IF NOT EXISTS health_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    age TEXT,
    weight TEXT,
    height TEXT,
    bp TEXT,
    sugar TEXT,
    smoking TEXT,
    family_history TEXT,
    extra_problems TEXT
)
''')



# Save changes
conn.commit()

# Close connection
conn.close()

print("Database & Table Created Successfully ✅")