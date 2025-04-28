import sqlite3
from app.utils import hash_password

# Connect to the SQLite database
conn = sqlite3.connect('./dreamapp.db')
cursor = conn.cursor()

# Get the user from the database
cursor.execute('SELECT * FROM users')
users = cursor.fetchall()
print("Current users:", users)

# Set a known password
new_password = "password123"
hashed_password = hash_password(new_password)

# Update the user's password
cursor.execute('UPDATE users SET hashed_password = ? WHERE email = ?', 
               (hashed_password, 'test@dream.com'))
conn.commit()

# Verify the update
cursor.execute('SELECT email, username, hashed_password FROM users')
updated_users = cursor.fetchall()
print("Updated users:", updated_users)

print(f"Password reset to '{new_password}' for user test@dream.com")

conn.close()