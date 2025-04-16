# import psycopg2
# from hashlib import sha256

# def get_db_connection():
#     conn = psycopg2.connect(
#         dbname="career_suite",  # Ensure this matches the actual database name
#         user="postgres",        # PostgreSQL username
#         password="956249",      # PostgreSQL password
#         host="localhost",       # PostgreSQL server address
#         port="5432"             # PostgreSQL port
#     )
#     return conn

# # Hashing function for passwords
# def hash_password(password):
#     return sha256(password.encode()).hexdigest()

# # Check user credentials
# def authenticate_user(username, password):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM client WHERE username = %s AND password = %s", 
#                    (username, hash_password(password)))
#     user = cursor.fetchone()
#     cursor.close()
#     conn.close()
#     return user is not None

# # Register a new user
# def register_user(username, password):
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     try:
#         cursor.execute("INSERT INTO client (username, password) VALUES (%s, %s)",
#                        (username, hash_password(password)))
#         conn.commit()
#     except psycopg2.IntegrityError:
#         conn.rollback()
#         return False
#     finally:
#         cursor.close()
#         conn.close()
#     return True







import json
import hashlib

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to authenticate user
def authenticate_user(username, password, users):
    if username in users and users[username] == hash_password(password):
        return True
    return False

# Function to register a new user
def register_user(username, password, users):
    if username in users:
        return False
    users[username] = hash_password(password)
    with open('users.json', 'w') as f:
        json.dump(users, f)
    return True
