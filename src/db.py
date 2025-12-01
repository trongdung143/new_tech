from src.setup import *
import psycopg2


connection = psycopg2.connect(
    user=USER, password=PASSWORD, host=HOST, port=PORT, dbname=DATABASE
)
