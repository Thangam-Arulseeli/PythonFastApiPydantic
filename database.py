# database.py --- For asynchronous database connection using psycopg 

from psycopg import AsyncConnection
from psycopg.rows import dict_row

from config import Config


async def get_connection():

    return await AsyncConnection.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        dbname=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
       row_factory=dict_row  # Then your repository becomes much easier to work with.
    )

'''
PostgreSQL returns rows.

By default, Psycopg returns each row as a tuple, which can be inconvenient to work with.
For example, if you have a row with columns id, name, and department_name, you would access the values like this:
row[0]  # id
row[1]  # name
row[2]  # department_name
(1, "Arun Kumar", "arun@gmail.com")

If you want to access the values by column name, you can use a row factory that returns each row as a dictionary instead of a tuple.[dict_row]
Because the above repository uses:

row["id"]
row["name"]
row["department_name"]

your database.py must use dict_row.
'''

### -----------------------------------------
# from psycopg import AsyncConnection

# from config import Config


# async def get_connection():

#     connection = await AsyncConnection.connect(
#         host=Config.DB_HOST,
#         port=Config.DB_PORT,
#         dbname=Config.DB_NAME,
#         user=Config.DB_USER,
#         password=Config.DB_PASSWORD
#     )

#     return connection