import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import Field, Session, select, SQLModel
from db import get_session
from models.Categories import Category
from models.Products import Product

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the media directory
app.mount("/media", StaticFiles(directory="media"), name="media")

# Operations
@app.get("/")
def root():
    return {"message": "Welcome to Mall Rats!"}

# Create
def create_generic(model):
    def create(item: SQLModel, session: Session = Depends(get_session)):
        session.add(item)
        session.commit()
        session.refresh(item)
        return item
    return create

# Read
def read_generic(model):
    def read(item_id: int, session: Session = Depends(get_session)):
        return session.get(model, item_id)
    return read

# Update
def update_generic(model):
    def update(item_id: int, item: SQLModel, session: Session = Depends(get_session)):
        db_item = session.get(model, item_id)
        if db_item:
            item_data = item.model_dump(exclude_unset=True)
            for key, value in item_data.items():
                setattr(db_item, key, value)
            session.add(db_item)
            session.commit()
            session.refresh(db_item)
            return db_item
        return {"error": f"{model.__name__} with id {item_id} not found"}
    return update

# Delete
def delete_generic(model):
    def delete(item_id: int, session: Session = Depends(get_session)):
        item = session.get(model, item_id)
        if item:
            session.delete(item)
            session.commit()
        return {"ok": True}
    return delete

@app.get("/api/products/")
async def get_products(category: str, db: Session = Depends(get_session)):
    try:
        query = select(Product, Category).join(Category, Product.subcategory_id == Category.id).where(Category.name.ilike(f"%{category}%"))
        
        results = db.exec(query).all()
        
        if not results:
            raise HTTPException(status_code=404, detail=f"No products found for category: {category}")
        
        return [{
            "name": product.name,
            "brand": product.brand,
            "price": product.price,
            "description": product.description,
            "image_url": product.image_url,
            "rating_value": product.rating_value,
            "rating_count": product.rating_count,
            "category_name": category.name
        } for product, category in results]
    except Exception as e:
        print(f"Error in get_products: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/categories/")
async def get_categories(db: Session = Depends(get_session)):
    try:
        query = select(Category)
        results = db.exec(query).all()
        return [{"name": category.name} for category in results]
    except Exception as e:
        print(f"Error in get_categories: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Categories CRUD
app.post("/categories/")(create_generic(Category))
app.get("/categories/{item_id}")(read_generic(Category))
app.put("/categories/{item_id}")(update_generic(Category))
app.delete("/categories/{item_id}")(delete_generic(Category))

# Products CRUD
app.post("/products/")(create_generic(Product))
app.get("/products/{item_id}")(read_generic(Product))
app.put("/products/{item_id}")(update_generic(Product))
app.delete("/products/{item_id}")(delete_generic(Product))

# Run the app
if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)