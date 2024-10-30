import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import Field, Session, select, SQLModel
from db import get_session, init_db
from models.categories import Category
from models.subcategories import SubCategory
from models.products import Product
from models.brands import Brand

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:5173",
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

# Mount the Media directory
app.mount("/media", StaticFiles(directory="../crudco/media"), name="media")

# Operations
@app.get("/")
def root():
    return {"message": "Snoochie Boochie Noochies!"}

# Generic CRUD operations remain the same
def create_generic(model):
    def create(item: model, session: Session = Depends(get_session)):
        try:
            data = item.model_dump(exclude={'id'})
            db_item = model(**data)
            session.add(db_item)
            session.commit()
            session.refresh(db_item)
            return db_item
        except Exception as e:
            session.rollback()
            print(f"Error creating {model.__name__}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error creating {model.__name__}: {str(e)}"
            )
    return create

def read_generic(model):
    def read(item_id: int, session: Session = Depends(get_session)):
        return session.get(model, item_id)
    return read

def update_generic(model):
    def update(item_id: int, item: model, session: Session = Depends(get_session)):
        db_item = session.get(model, item_id)
        if db_item:
            item_data = item.model_dump(exclude={'id'}, exclude_unset=True)
            for key, value in item_data.items():
                setattr(db_item, key, value)
            session.add(db_item)
            session.commit()
            session.refresh(db_item)
            return db_item
        return {"error": f"{model.__name__} with id {item_id} not found"}
    return update

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
        query = select(Product, SubCategory, Category, Brand).join(
            SubCategory, Product.subcategory_id == SubCategory.id
        ).join(
            Category, SubCategory.category_id == Category.id
        ).join(
            Brand, Product.brand_id == Brand.id
        ).where(Category.name.ilike(f"%{category}%"))
        
        results = db.exec(query).all()
        
        if not results:
            raise HTTPException(status_code=404, detail=f"No products found for category: {category}")
        
        return [{
            "name": product.name,
            "brand_id": product.brand_id,
            "brand_name": brand.name,
            "price": product.price,
            "description": product.description,
            "image_url": product.image_url,
            "rating_value": product.rating_value,
            "rating_count": product.rating_count,
            "category_name": category.name,
            "subcategory_name": subcategory.name
        } for product, subcategory, category, brand in results]
    except Exception as e:
        print(f"Error in get_products: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/brands/")
async def get_brands(db: Session = Depends(get_session)):
    try:
        query = select(Brand)
        results = db.exec(query).all()
        return [{"id": brand.id, "name": brand.name} for brand in results]
    except Exception as e:
        print(f"Error in get_brands: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Existing routes remain the same
@app.get("/api/categories/")
async def get_categories(db: Session = Depends(get_session)):
    try:
        query = select(Category)
        results = db.exec(query).all()
        return [{"id": category.id, "name": category.name, "emoji": category.emoji} for category in results]
    except Exception as e:
        print(f"Error in get_categories: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/subcategories/")
async def get_subcategories(category_id: int = None, db: Session = Depends(get_session)):
    try:
        query = select(SubCategory, Category).join(Category, SubCategory.category_id == Category.id)
        if category_id:
            query = query.where(SubCategory.category_id == category_id)
        results = db.exec(query).all()
        return [{
            "id": subcategory.id,
            "name": subcategory.name,
            "category_id": subcategory.category_id,
            "category_name": category.name
        } for subcategory, category in results]
    except Exception as e:
        print(f"Error in get_subcategories: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Categories CRUD
app.post("/categories/")(create_generic(Category))
app.get("/categories/{item_id}")(read_generic(Category))
app.put("/categories/{item_id}")(update_generic(Category))
app.delete("/categories/{item_id}")(delete_generic(Category))

# Subcategories CRUD
app.post("/subcategories/")(create_generic(SubCategory))
app.get("/subcategories/{item_id}")(read_generic(SubCategory))
app.put("/subcategories/{item_id}")(update_generic(SubCategory))
app.delete("/subcategories/{item_id}")(delete_generic(SubCategory))

# Products CRUD
app.post("/products/")(create_generic(Product))
app.get("/products/{item_id}")(read_generic(Product))
app.put("/products/{item_id}")(update_generic(Product))
app.delete("/products/{item_id}")(delete_generic(Product))

# Brands CRUD
app.post("/brands/")(create_generic(Brand))
app.get("/brands/{item_id}")(read_generic(Brand))
app.put("/brands/{item_id}")(update_generic(Brand))
app.delete("/brands/{item_id}")(delete_generic(Brand))

# Initialize database
@app.on_event("startup")
async def on_startup():
    init_db()

# Run the app
if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)