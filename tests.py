try:
    import requests
    print("requests is installed!")
except ImportError:
    print("requests is NOT installed!")

try:
    import flask
    print("flask is installed!")
except ImportError:
    print("flask is NOT installed!")

try:
    import pytest
    print("pytest is installed!")
except ImportError:
    print("pytest is NOT installed!")


import psycopg2

conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="NewStrongPassword",
    host="localhost",
    port=5432
)

print("Connected!")
conn.close()
