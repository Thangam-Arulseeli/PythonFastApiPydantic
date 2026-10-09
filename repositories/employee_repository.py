# repositories/employee_repository.py 
# --- For asynchronous database operations related to employees
### Now the repository communicates only with PostgreSQL.

# Creating a repository layer to handle database operations for employees.
#  This layer will interact with the database using the `database.py` module,
#  which provides an asynchronous connection to PostgreSQL.

# The repository will contain functions to perform CRUD operations on the employees table.

# This does the following::
# Create employee
# Get employee by ID
# Get all employees
# Pagination
# Department filtering
# Department JOIN
# Update employee
# Delete employee
# Update photo/resume paths
# Check email
# dict_row


from database import get_connection

# =========================================================
# CREATE EMPLOYEE
# =========================================================

async def create_employee(
    name: str,
    email: str,
    department_id: int,
    designation: str,
    salary: float,
    status: str,
    street: str | None,
    city: str | None,
    state: str | None,
    pincode: str | None
):

    async with await get_connection() as connection:

        async with connection.cursor() as cursor:

            await cursor.execute(
                """
                INSERT INTO employees
                (
                    name,
                    email,
                    department_id,
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
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                RETURNING
                    id,
                    name,
                    email,
                    department_id,
                    designation,
                    salary,
                    status,
                    street,
                    city,
                    state,
                    pincode,
                    photo_path,
                    resume_path
                """,
                (
                    name,
                    email,
                    department_id,
                    designation,
                    salary,
                    status,
                    street,
                    city,
                    state,
                    pincode
                )
            )

            employee = await cursor.fetchone()

            await connection.commit()

            return employee


# =========================================================
# GET EMPLOYEE BY ID
# =========================================================

async def get_employee_by_id(
    employee_id: int
):

    async with await get_connection() as connection:

        async with connection.cursor() as cursor:

            await cursor.execute(
                """
                SELECT
                    e.id,
                    e.name,
                    e.email,
                    e.department_id,
                    e.designation,
                    e.salary,
                    e.status,

                    e.street,
                    e.city,
                    e.state,
                    e.pincode,

                    e.photo_path,
                    e.resume_path,

                    d.id AS department_ref_id,
                    d.name AS department_name,
                    d.description AS department_description,
                    d.is_active AS department_is_active

                FROM employees e

                INNER JOIN departments d
                    ON e.department_id = d.id

                WHERE e.id = %s
                """,
                (employee_id,)
            )

            return await cursor.fetchone()


# =========================================================
# GET TOTAL EMPLOYEE COUNT
# =========================================================

async def get_employee_count(
    department_id: int | None = None
):

    async with await get_connection() as connection:

        async with connection.cursor() as cursor:

            if department_id is None:

                await cursor.execute(
                    """
                    SELECT COUNT(*) AS total
                    FROM employees
                    """
                )

            else:

                await cursor.execute(
                    """
                    SELECT COUNT(*) AS total
                    FROM employees
                    WHERE department_id = %s
                    """,
                    (department_id,)
                )

            result = await cursor.fetchone()

            return result["total"]


# =========================================================
# GET ALL EMPLOYEES
#
# Supports:
#   pagination
#   department filtering
# =========================================================

async def get_all_employees(
    page: int,
    page_size: int,
    department_id: int | None = None
):

    offset = (page - 1) * page_size

    async with await get_connection() as connection:

        async with connection.cursor() as cursor:

            if department_id is None:

                await cursor.execute(
                    """
                    SELECT
                        e.id,
                        e.name,
                        e.email,
                        e.department_id,
                        e.designation,
                        e.salary,
                        e.status,

                        e.street,
                        e.city,
                        e.state,
                        e.pincode,

                        e.photo_path,
                        e.resume_path,

                        d.id AS department_ref_id,
                        d.name AS department_name,
                        d.description AS department_description,
                        d.is_active AS department_is_active

                    FROM employees e

                    INNER JOIN departments d
                        ON e.department_id = d.id

                    ORDER BY e.id

                    LIMIT %s
                    OFFSET %s
                    """,
                    (
                        page_size,
                        offset
                    )
                )

            else:

                await cursor.execute(
                    """
                    SELECT
                        e.id,
                        e.name,
                        e.email,
                        e.department_id,
                        e.designation,
                        e.salary,
                        e.status,

                        e.street,
                        e.city,
                        e.state,
                        e.pincode,

                        e.photo_path,
                        e.resume_path,

                        d.id AS department_ref_id,
                        d.name AS department_name,
                        d.description AS department_description,
                        d.is_active AS department_is_active

                    FROM employees e

                    INNER JOIN departments d
                        ON e.department_id = d.id

                    WHERE e.department_id = %s

                    ORDER BY e.id

                    LIMIT %s
                    OFFSET %s
                    """,
                    (
                        department_id,
                        page_size,
                        offset
                    )
                )

            return await cursor.fetchall()


# =========================================================
# CHECK EMAIL EXISTS
# =========================================================

async def email_exists(
    email: str,
    exclude_employee_id: int | None = None
):

    async with await get_connection() as connection:

        async with connection.cursor() as cursor:

            if exclude_employee_id is None:

                await cursor.execute(
                    """
                    SELECT EXISTS
                    (
                        SELECT 1
                        FROM employees
                        WHERE LOWER(email) = LOWER(%s)
                    ) AS exists
                    """,
                    (email,)
                )

            else:

                await cursor.execute(
                    """
                    SELECT EXISTS
                    (
                        SELECT 1
                        FROM employees
                        WHERE LOWER(email) = LOWER(%s)
                        AND id <> %s
                    ) AS exists
                    """,
                    (
                        email,
                        exclude_employee_id
                    )
                )

            result = await cursor.fetchone()

            return result["exists"]


# =========================================================
# UPDATE EMPLOYEE
# =========================================================

async def update_employee(
    employee_id: int,
    name: str | None,
    email: str | None,
    department_id: int | None,
    designation: str | None,
    salary: float | None,
    status: str | None,
    street: str | None,
    city: str | None,
    state: str | None,
    pincode: str | None
):

    async with await get_connection() as connection:

        async with connection.cursor() as cursor:

            await cursor.execute(
                """
                UPDATE employees
                SET
                    name = COALESCE(%s, name),
                    email = COALESCE(%s, email),
                    department_id = COALESCE(%s, department_id),
                    designation = COALESCE(%s, designation),
                    salary = COALESCE(%s, salary),
                    status = COALESCE(%s, status),
                    street = COALESCE(%s, street),
                    city = COALESCE(%s, city),
                    state = COALESCE(%s, state),
                    pincode = COALESCE(%s, pincode)

                WHERE id = %s

                RETURNING
                    id,
                    name,
                    email,
                    department_id,
                    designation,
                    salary,
                    status,
                    street,
                    city,
                    state,
                    pincode,
                    photo_path,
                    resume_path
                """,
                (
                    name,
                    email,
                    department_id,
                    designation,
                    salary,
                    status,
                    street,
                    city,
                    state,
                    pincode,
                    employee_id
                )
            )

            employee = await cursor.fetchone()

            await connection.commit()

            return employee


# =========================================================
# DELETE EMPLOYEE
# =========================================================

async def delete_employee(
    employee_id: int
):

    async with await get_connection() as connection:

        async with connection.cursor() as cursor:

            await cursor.execute(
                """
                DELETE FROM employees
                WHERE id = %s
                RETURNING id
                """,
                (employee_id,)
            )

            deleted_employee = await cursor.fetchone()

            await connection.commit()

            return deleted_employee


# =========================================================
# UPDATE PHOTO / RESUME
# =========================================================

async def update_employee_files(
    employee_id: int,
    photo_path: str | None = None,
    resume_path: str | None = None
):

    async with await get_connection() as connection:

        async with connection.cursor() as cursor:

            await cursor.execute(
                """
                UPDATE employees
                SET
                    photo_path = COALESCE(
                        %s,
                        photo_path
                    ),

                    resume_path = COALESCE(
                        %s,
                        resume_path
                    )

                WHERE id = %s

                RETURNING
                    id,
                    photo_path,
                    resume_path
                """,
                (
                    photo_path,
                    resume_path,
                    employee_id
                )
            )

            employee = await cursor.fetchone()

            await connection.commit()

            return employee



#==================================================
# from database import get_connection

# # Get all employees from the database
# async def get_all_employees():

#     connection = await get_connection()

#     try:

#         async with connection.cursor() as cursor:

#             await cursor.execute("""
#                 SELECT
#                     id,
#                     name,
#                     email,
#                     department,
#                     designation,
#                     salary,
#                     status,
#                     street,
#                     city,
#                     state,
#                     pincode
#                 FROM employees
#                 ORDER BY id
#             """)

#             rows = await cursor.fetchall()

#             return rows

#     finally:

#         await connection.close()
# # -----------------------------------------

# # Get an employee by ID from the database
# async def get_employee_by_id(employee_id: int):

#     connection = await get_connection()

#     try:

#         async with connection.cursor() as cursor:

#             await cursor.execute("""
#                 SELECT
#                     id,
#                     name,
#                     email,
#                     department,
#                     designation,
#                     salary,
#                     status,
#                     street,
#                     city,
#                     state,
#                     pincode
#                 FROM employees
#                 WHERE id = %s
#             """, (employee_id,))

#             return await cursor.fetchone()

#     finally:

#         await connection.close()
#     # -----------------------------------------

# # Add a new employee to the database  --- With Department table relation (1:N relation)

# async def insert_employee(data: dict):

#     connection = await get_connection()

#     try:

#         async with connection.cursor() as cursor:

#             await cursor.execute("""
#                 INSERT INTO employees
#                 (
#                     name,
#                     email,
#                     department_id,
#                     designation,
#                     salary,
#                     status,
#                     street,
#                     city,
#                     state,
#                     pincode
#                 )
#                 VALUES
#                 (
#                     %s, %s, %s, %s, %s,
#                     %s, %s, %s, %s, %s
#                 )
#                 RETURNING id
#             """, (
#                 data["name"],
#                 data["email"],
#                 data["department_id"],
#                 data["designation"],
#                 data["salary"],
#                 data["status"],
#                 data["address"]["street"],
#                 data["address"]["city"],
#                 data["address"]["state"],
#                 data["address"]["pincode"]
#             ))

#             employee_id = (
#                 await cursor.fetchone()
#             )[0]

#             await connection.commit()

#             return employee_id

#     except Exception:

#         await connection.rollback()

#         raise

#     finally:

#         await connection.close()


# # ----------------
# # async def insert_employee(data: dict):

# #     connection = await get_connection()

# #     try:

# #         async with connection.cursor() as cursor:

# #             await cursor.execute("""
# #                 INSERT INTO employees
# #                 (
# #                     name,
# #                     email,
# #                     department,
# #                     designation,
# #                     salary,
# #                     status,
# #                     street,
# #                     city,
# #                     state,
# #                     pincode
# #                 )
# #                 VALUES
# #                 (
# #                     %s, %s, %s, %s, %s,
# #                     %s, %s, %s, %s, %s
# #                 )
# #                 RETURNING
# #                     id,
# #                     name,
# #                     email,
# #                     department,
# #                     designation,
# #                     salary,
# #                     status,
# #                     street,
# #                     city,
# #                     state,
# #                     pincode
# #             """, (
# #                 data["name"],
# #                 data["email"],
# #                 data["department"],
# #                 data["designation"],
# #                 data["salary"],
# #                 data["status"],
# #                 data["address"]["street"],
# #                 data["address"]["city"],
# #                 data["address"]["state"],
# #                 data["address"]["pincode"]
# #             ))

# #             row = await cursor.fetchone()

# #             await connection.commit()

# #             return row

# #     except Exception:

# #         await connection.rollback()

# #         raise

# #     finally:

# #         await connection.close()
# # ----------------------------------------------

# # Update an existing employee in the database
# async def update_employee(
#     employee_id: int,
#     data: dict
# ):

#     connection = await get_connection()

#     try:

#         async with connection.cursor() as cursor:

#             await cursor.execute("""
#                 UPDATE employees
#                 SET
#                     name = %s,
#                     email = %s,
#                     department = %s,
#                     designation = %s,
#                     salary = %s,
#                     status = %s,
#                     street = %s,
#                     city = %s,
#                     state = %s,
#                     pincode = %s
#                 WHERE id = %s
#                 RETURNING
#                     id,
#                     name,
#                     email,
#                     department,
#                     designation,
#                     salary,
#                     status,
#                     street,
#                     city,
#                     state,
#                     pincode
#             """, (
#                 data["name"],
#                 data["email"],
#                 data["department"],
#                 data["designation"],
#                 data["salary"],
#                 data["status"],
#                 data["address"]["street"],
#                 data["address"]["city"],
#                 data["address"]["state"],
#                 data["address"]["pincode"],
#                 employee_id
#             ))

#             row = await cursor.fetchone()

#             if row is None:

#                 await connection.rollback()

#                 return None

#             await connection.commit()

#             return row

#     except Exception:

#         await connection.rollback()

#         raise

#     finally:

#         await connection.close()
# # ----------------------------------------------

# # Delete an employee from the database
# async def delete_employee(employee_id: int):

#     connection = await get_connection()

#     try:

#         async with connection.cursor() as cursor:

#             await cursor.execute("""
#                 DELETE FROM employees
#                 WHERE id = %s
#                 RETURNING id
#             """, (employee_id,))

#             row = await cursor.fetchone()

#             if row is None:

#                 await connection.rollback()

#                 return None

#             await connection.commit()

#             return row[0]

#     except Exception:

#         await connection.rollback()

#         raise

#     finally:

#         await connection.close()
# # ---------------------------------------

