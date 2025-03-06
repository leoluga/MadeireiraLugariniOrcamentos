# main.py

from fastapi import FastAPI
from infrastructure.database import Base, engine
from routers.wood_router import router as wood_router
from routers.orcamento_router import router as orcamento_router

# Create DB tables (if not using migrations)
Base.metadata.create_all(bind=engine)

# Initialize the FastAPI application
app = FastAPI(title="Wood Orçamento API")

# Include routers
app.include_router(wood_router)
app.include_router(orcamento_router)

@app.get("/")
def root():
    return {"message": "Welcome to the Wood Orçamento API!"}
