# database.py --- For asynchronous database connection using psycopg 
from psycopg import AsyncConnection

from config import Config


async def get_connection():

    connection = await AsyncConnection.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        dbname=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD
    )

    return connection