from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session as DBSession

from models import Product  # Pydantic model
from database import Session, engine
import database_models

app = FastAPI()

# Create tables
database_models.Base.metadata.create_all(bind=engine)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# ✅ Dependency (BEST PRACTICE)
# -------------------------------
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


# -------------------------------
# ✅ Initial Data
# -------------------------------
products_seed = [
    Product(id=1, name="Phone", description="A smartphone", price=699.99, quantity=50),
    Product(id=2, name="Laptop", description="A powerful laptop", price=999.99, quantity=30),
    Product(id=3, name="Pen", description="A blue ink pen", price=1.99, quantity=100),
    Product(id=4, name="Table", description="A wooden table", price=199.99, quantity=20),
]


def init_db():
    db = Session()
    existing = db.query(database_models.Product).first()

    if not existing:
        for p in products_seed:
            db.add(database_models.Product(**p.model_dump()))
        db.commit()

    db.close()


# Run on startup
@app.on_event("startup")
def startup_event():
    init_db()


# -------------------------------
# ✅ Routes
# -------------------------------

@app.get("/")
def greet():
    return {"message": "Hello Varun 🚀"}


# -------------------------------
# GET ALL PRODUCTS
# -------------------------------
@app.get("/products")
def get_all_products(db: DBSession = Depends(get_db)):
    return db.query(database_models.Product).all()


# -------------------------------
# GET PRODUCT BY ID
# -------------------------------
@app.get("/products/{id}")
def get_product(id: int, db: DBSession = Depends(get_db)):
    product = db.query(database_models.Product).filter(database_models.Product.id == id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


# -------------------------------
# ADD PRODUCT
# -------------------------------
@app.post("/products")
def add_product(product_new: Product, db: DBSession = Depends(get_db)):
    db_product = database_models.Product(**product_new.model_dump())

    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    return {"message": "Product added", "data": db_product}


# -------------------------------
# UPDATE PRODUCT
# -------------------------------
@app.put("/products/{id}")
def update_product(id: int, product_update: Product, db: DBSession = Depends(get_db)):
    product = db.query(database_models.Product).filter(database_models.Product.id == id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    for key, value in product_update.model_dump().items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)

    return {"message": "Product updated", "data": product}


# -------------------------------
# DELETE PRODUCT
# -------------------------------
@app.delete("/products/{id}")
def delete_product(id: int, db: DBSession = Depends(get_db)):
    product = db.query(database_models.Product).filter(database_models.Product.id == id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()

    return {"message": "Product deleted"}