from fastapi import FastAPI

from routers.employee_router import router as employee_router
from routers.department_router import router as department_router


app = FastAPI(
    title="Employee Management API",
    version="2.0.0"
)


@app.get("/")
async def home():

    return {
        "message": "Employee API is running"
    }

app.include_router(department_router)

app.include_router(employee_router)


#----------------------------------------
# from fastapi import FastAPI

# from routers.employee_router import router as employee_router

# app = FastAPI(
#     title="Employee Management API",
#     description="FastAPI + PostgreSQL CRUD",
#     version="1.0.0"
# )

# app.include_router(
#     employee_router
# )

# @app.get("/")
# async def home():

#     return {
#         "message": "Employee API is running"
#     }
