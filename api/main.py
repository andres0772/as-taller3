from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from api.database import get_db
from api.routes import users, products, carts

# Crear la instancia de FastAPI
app = FastAPI(title="Tienda Virtual API", version="1.0.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir los routers
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(products.router, prefix="/api/v1/products", tags=["products"])
app.include_router(carts.router, prefix="/api/v1/carts", tags=["carts"])

@app.get("/")
async def root():
    # Endpoint de prueba
    return {"message": "Tienda Virtual API", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
