# Department Repository: This file contains functions to interact with the departments table 
# in # the database.
# This module should contain database-related operations only. It should NOT contain business  # rules.

'''
Recommended department_repository.py using dict_row
-----------------------------------------------------

If you are using dict_row, use this version instead of the previous repository code:


For example:
-------------

department = await cursor.fetchone()

returns:

{
    "id": 1,
    "name": "Development",
    "description": "Software development team",
    "is_active": True
}

instead of:

(1, "Development", "Software development team", True)

That eliminates many row[0], row[1] errors.

'''

from database import get_connection


# =========================================================
# CREATE DEPARTMENT
# =========================================================

async def create_department(
    name: str,
    description: str | None
):

    async with await get_connection() as connection:

        async with connection.cursor() as cursor:

            await cursor.execute(
                """
                INSERT INTO departments
                (
                    name,
                    description
                )
                VALUES
                (
                    %s,
                    %s
                )
                RETURNING
                    id,
                    name,
                    description,
                    is_active
                """,
                (
                    name,
                    description
                )
            )

            department = await cursor.fetchone()

            await connection.commit()

            return department


# =========================================================
# GET DEPARTMENT BY ID
# =========================================================

async def get_department_by_id(
    department_id: int
):

    async with await get_connection() as connection:

        async with connection.cursor() as cursor:

            await cursor.execute(
                """
                SELECT
                    id,
                    name,
                    description,
                    is_active
                FROM departments
                WHERE id = %s
                """,
                (department_id,)
            )

            return await cursor.fetchone()


# =========================================================
# GET ALL DEPARTMENTS
# =========================================================

async def get_all_departments():

    async with await get_connection() as connection:

        async with connection.cursor() as cursor:

            await cursor.execute(
                """
                SELECT
                    id,
                    name,
                    description,
                    is_active
                FROM departments
                ORDER BY id
                """
            )

            return await cursor.fetchall()


# =========================================================
# UPDATE DEPARTMENT
# =========================================================

async def update_department(
    department_id: int,
    name: str | None,
    description: str | None,
    is_active: bool | None
):

    async with await get_connection() as connection:

        async with connection.cursor() as cursor:

            await cursor.execute(
                """
                UPDATE departments
                SET
                    name = COALESCE(%s, name),
                    description = COALESCE(%s, description),
                    is_active = COALESCE(%s, is_active)
                WHERE id = %s
                RETURNING
                    id,
                    name,
                    description,
                    is_active
                """,
                (
                    name,
                    description,
                    is_active,
                    department_id
                )
            )

            department = await cursor.fetchone()

            await connection.commit()

            return department


# =========================================================
# DELETE DEPARTMENT
# =========================================================

async def delete_department(
    department_id: int
):

    async with await get_connection() as connection:

        async with connection.cursor() as cursor:

            await cursor.execute(
                """
                DELETE FROM departments
                WHERE id = %s
                RETURNING id
                """,
                (department_id,)
            )

            deleted_department = await cursor.fetchone()

            await connection.commit()

            return deleted_department


# =========================================================
# CHECK DEPARTMENT EXISTS
# =========================================================

async def department_exists(
    department_id: int
):

    async with await get_connection() as connection:

        async with connection.cursor() as cursor:

            await cursor.execute(
                """
                SELECT EXISTS
                (
                    SELECT 1
                    FROM departments
                    WHERE id = %s
                )
                """,
                (department_id,)
            )

            result = await cursor.fetchone()

            return result["exists"]


# =========================================================
# CHECK DEPARTMENT NAME EXISTS
# =========================================================

async def department_name_exists(
    name: str,
    exclude_department_id: int | None = None
):

    async with await get_connection() as connection:

        async with connection.cursor() as cursor:

            if exclude_department_id is None:

                await cursor.execute(
                    """
                    SELECT EXISTS
                    (
                        SELECT 1
                        FROM departments
                        WHERE LOWER(name) = LOWER(%s)
                    ) AS exists
                    """,
                    (name,)
                )

            else:

                await cursor.execute(
                    """
                    SELECT EXISTS
                    (
                        SELECT 1
                        FROM departments
                        WHERE LOWER(name) = LOWER(%s)
                        AND id <> %s
                    ) AS exists
                    """,
                    (
                        name,
                        exclude_department_id
                    )
                )

            result = await cursor.fetchone()

            return result["exists"]


# =========================================================
# CHECK WHETHER DEPARTMENT HAS EMPLOYEES
# =========================================================

async def department_has_employees(
    department_id: int
):

    async with await get_connection() as connection:

        async with connection.cursor() as cursor:

            await cursor.execute(
                """
                SELECT EXISTS
                (
                    SELECT 1
                    FROM employees
                    WHERE department_id = %s
                ) AS exists
                """,
                (department_id,)
            )

            result = await cursor.fetchone()

            return result["exists"]


# =========================================================
# GET EMPLOYEES BY DEPARTMENT
# =========================================================

async def get_employees_by_department(
    department_id: int
):

    async with await get_connection() as connection:

        async with connection.cursor() as cursor:

            await cursor.execute(
                """
                SELECT
                    e.id,
                    e.name,
                    e.email,
                    e.designation,
                    e.salary,
                    e.status
                FROM employees e
                INNER JOIN departments d
                    ON e.department_id = d.id
                WHERE d.id = %s
                ORDER BY e.id
                """,
                (department_id,)
            )

            return await cursor.fetchall()
# ======================================================



#### Without dict_row, use this version instead of the previous repository code:
'''
from database import get_connection


# =========================================================
# CREATE DEPARTMENT
# =========================================================

async def create_department(
    name: str,
    description: str | None
):

    async with await get_connection() as connection:

        async with connection.cursor() as cursor:

            await cursor.execute(
                """
                INSERT INTO departments
                (
                    name,
                    description
                )
                VALUES
                (
                    %s,
                    %s
                )
                RETURNING
                    id,
                    name,
                    description,
                    is_active
                """,
                (
                    name,
                    description
                )
            )

            department = await cursor.fetchone()

            await connection.commit()

            return department


# =========================================================
# GET DEPARTMENT BY ID
# =========================================================

async def get_department_by_id(
    department_id: int
):

    async with await get_connection() as connection:

        async with connection.cursor() as cursor:

            await cursor.execute(
                """
                SELECT
                    id,
                    name,
                    description,
                    is_active
                FROM departments
                WHERE id = %s
                """,
                (department_id,)
            )

            return await cursor.fetchone()


# =========================================================
# GET ALL DEPARTMENTS
# =========================================================

async def get_all_departments():

    async with await get_connection() as connection:

        async with connection.cursor() as cursor:

            await cursor.execute(
                """
                SELECT
                    id,
                    name,
                    description,
                    is_active
                FROM departments
                ORDER BY id
                """
            )

            return await cursor.fetchall()


# =========================================================
# UPDATE DEPARTMENT
# =========================================================

async def update_department(
    department_id: int,
    name: str | None,
    description: str | None,
    is_active: bool | None
):

    async with await get_connection() as connection:

        async with connection.cursor() as cursor:

            await cursor.execute(
                """
                UPDATE departments
                SET
                    name = COALESCE(%s, name),
                    description = COALESCE(%s, description),
                    is_active = COALESCE(%s, is_active)
                WHERE id = %s
                RETURNING
                    id,
                    name,
                    description,
                    is_active
                """,
                (
                    name,
                    description,
                    is_active,
                    department_id
                )
            )

            department = await cursor.fetchone()

            await connection.commit()

            return department


# =========================================================
# DELETE DEPARTMENT
# =========================================================

async def delete_department(
    department_id: int
):

    async with await get_connection() as connection:

        async with connection.cursor() as cursor:

            await cursor.execute(
                """
                DELETE FROM departments
                WHERE id = %s
                RETURNING id
                """,
                (department_id,)
            )

            deleted_department = await cursor.fetchone()

            await connection.commit()

            return deleted_department


# =========================================================
# CHECK DEPARTMENT EXISTS
# =========================================================

async def department_exists(
    department_id: int
):

    async with await get_connection() as connection:

        async with connection.cursor() as cursor:

            await cursor.execute(
                """
                SELECT EXISTS
                (
                    SELECT 1
                    FROM departments
                    WHERE id = %s
                )
                """,
                (department_id,)
            )

            result = await cursor.fetchone()

            return result[0]


# =========================================================
# CHECK DEPARTMENT NAME EXISTS
# =========================================================

async def department_name_exists(
    name: str,
    exclude_department_id: int | None = None
):

    async with await get_connection() as connection:

        async with connection.cursor() as cursor:

            if exclude_department_id is None:

                await cursor.execute(
                    """
                    SELECT EXISTS
                    (
                        SELECT 1
                        FROM departments
                        WHERE LOWER(name) = LOWER(%s)
                    )
                    """,
                    (name,)
                )

            else:

                await cursor.execute(
                    """
                    SELECT EXISTS
                    (
                        SELECT 1
                        FROM departments
                        WHERE LOWER(name) = LOWER(%s)
                        AND id <> %s
                    )
                    """,
                    (
                        name,
                        exclude_department_id
                    )
                )

            result = await cursor.fetchone()

            return result[0]


# =========================================================
# CHECK WHETHER DEPARTMENT HAS EMPLOYEES
# =========================================================

async def department_has_employees(
    department_id: int
):

    async with await get_connection() as connection:

        async with connection.cursor() as cursor:

            await cursor.execute(
                """
                SELECT EXISTS
                (
                    SELECT 1
                    FROM employees
                    WHERE department_id = %s
                )
                """,
                (department_id,)
            )

            result = await cursor.fetchone()

            return result[0]


# =========================================================
# GET EMPLOYEES BY DEPARTMENT
# =========================================================

async def get_employees_by_department(
    department_id: int
):

    async with await get_connection() as connection:

        async with connection.cursor() as cursor:

            await cursor.execute(
                """
                SELECT
                    e.id,
                    e.name,
                    e.email,
                    e.designation,
                    e.salary,
                    e.status
                FROM employees e
                INNER JOIN departments d
                    ON e.department_id = d.id
                WHERE d.id = %s
                ORDER BY e.id
                """,
                (department_id,)
            )

            return await cursor.fetchall()
'''        
# # -----------------------------------------



# -------------------------------------------
# from database import get_connection

# async def get_department_by_id(
#     department_id: int
# ):

#     connection = await get_connection()

#     try:

#         async with connection.cursor() as cursor:

#             await cursor.execute("""
#                 SELECT
#                     id,
#                     name,
#                     description,
#                     is_active
#                 FROM departments
#                 WHERE id = %s
#             """, (department_id,))

#             return await cursor.fetchone()

#     finally:

#         await connection.close()

