from fastapi import FastAPI

from routers.employee_router import router as employee_router

app = FastAPI(
    title="Employee Management API",
    description="FastAPI + PostgreSQL CRUD",
    version="1.0.0"
)

app.include_router(
    employee_router
)

@app.get("/")
async def home():

    return {
        "message": "Employee API is running"
    }
