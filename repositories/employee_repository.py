# repositories/employee_repository.py 
# --- For asynchronous database operations related to employees
### Now the repository communicates only with PostgreSQL.

# Creating a repository layer to handle database operations for employees.
#  This layer will interact with the database using the `database.py` module,
#  which provides an asynchronous connection to PostgreSQL.

# The repository will contain functions to perform CRUD operations on the employees table.


from database import get_connection

# Get all employees from the database
async def get_all_employees():

    connection = await get_connection()

    try:

        async with connection.cursor() as cursor:

            await cursor.execute("""
                SELECT
                    id,
                    name,
                    email,
                    department,
                    designation,
                    salary,
                    status,
                    street,
                    city,
                    state,
                    pincode
                FROM employees
                ORDER BY id
            """)

            rows = await cursor.fetchall()

            return rows

    finally:

        await connection.close()
# -----------------------------------------

# Get an employee by ID from the database
async def get_employee_by_id(employee_id: int):

    connection = await get_connection()

    try:

        async with connection.cursor() as cursor:

            await cursor.execute("""
                SELECT
                    id,
                    name,
                    email,
                    department,
                    designation,
                    salary,
                    status,
                    street,
                    city,
                    state,
                    pincode
                FROM employees
                WHERE id = %s
            """, (employee_id,))

            return await cursor.fetchone()

    finally:

        await connection.close()
    # -----------------------------------------

# Add a new employee to the database
async def insert_employee(data: dict):

    connection = await get_connection()

    try:

        async with connection.cursor() as cursor:

            await cursor.execute("""
                INSERT INTO employees
                (
                    name,
                    email,
                    department,
                    designation,
                    salary,
                    status,
                    street,
                    city,
                    state,
                    pincode
                )
                VALUES
                (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
                )
                RETURNING
                    id,
                    name,
                    email,
                    department,
                    designation,
                    salary,
                    status,
                    street,
                    city,
                    state,
                    pincode
            """, (
                data["name"],
                data["email"],
                data["department"],
                data["designation"],
                data["salary"],
                data["status"],
                data["address"]["street"],
                data["address"]["city"],
                data["address"]["state"],
                data["address"]["pincode"]
            ))

            row = await cursor.fetchone()

            await connection.commit()

            return row

    except Exception:

        await connection.rollback()

        raise

    finally:

        await connection.close()
# ----------------------------------------------

# Update an existing employee in the database
async def update_employee(
    employee_id: int,
    data: dict
):

    connection = await get_connection()

    try:

        async with connection.cursor() as cursor:

            await cursor.execute("""
                UPDATE employees
                SET
                    name = %s,
                    email = %s,
                    department = %s,
                    designation = %s,
                    salary = %s,
                    status = %s,
                    street = %s,
                    city = %s,
                    state = %s,
                    pincode = %s
                WHERE id = %s
                RETURNING
                    id,
                    name,
                    email,
                    department,
                    designation,
                    salary,
                    status,
                    street,
                    city,
                    state,
                    pincode
            """, (
                data["name"],
                data["email"],
                data["department"],
                data["designation"],
                data["salary"],
                data["status"],
                data["address"]["street"],
                data["address"]["city"],
                data["address"]["state"],
                data["address"]["pincode"],
                employee_id
            ))

            row = await cursor.fetchone()

            if row is None:

                await connection.rollback()

                return None

            await connection.commit()

            return row

    except Exception:

        await connection.rollback()

        raise

    finally:

        await connection.close()
# ----------------------------------------------

# Delete an employee from the database
async def delete_employee(employee_id: int):

    connection = await get_connection()

    try:

        async with connection.cursor() as cursor:

            await cursor.execute("""
                DELETE FROM employees
                WHERE id = %s
                RETURNING id
            """, (employee_id,))

            row = await cursor.fetchone()

            if row is None:

                await connection.rollback()

                return None

            await connection.commit()

            return row[0]

    except Exception:

        await connection.rollback()

        raise

    finally:

        await connection.close()
# ---------------------------------------

