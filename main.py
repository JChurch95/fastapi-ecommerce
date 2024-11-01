import uvicorn
import jwt
from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Field, Session, select, SQLModel
from db import get_session, init_db
from config import SUPABASE_SECRET_KEY, JWT_ALGORITHM

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

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SUPABASE_SECRET_KEY,
                             audience=["authenticated"],
                             algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# Operations
@app.get("/")
def root():
    return {"message": "Snoochie Boochie Noochies!"}



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



# Products CRUD with new authenticated add endpoint
@app.post("/products/add")
async def add_product(
    product: Product, 
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())],
    session: Session = Depends(get_session)
):
    if not credentials:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    # Verify the token
    verify_token(credentials.credentials)
    
    try:
        # Exclude id when creating new product
        product_data = product.model_dump(exclude={'id'})
        db_product = Product(**product_data)
        session.add(db_product)
        session.commit()
        session.refresh(db_product)
        return {"message": f"Product Added: {db_product.name}", "product": db_product}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating product: {str(e)}")
    



# Categories authenticated CRUD
@app.post("/categories/auth/add")
async def add_category(
    category: Category,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())],
    session: Session = Depends(get_session)
):
    if not credentials:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    verify_token(credentials.credentials)
    
    try:
        category_data = category.model_dump(exclude={'id'})
        db_category = Category(**category_data)
        session.add(db_category)
        session.commit()
        session.refresh(db_category)
        return {"message": f"Category Added: {db_category.name}", "category": db_category}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating category: {str(e)}")



@app.put("/categories/auth/{item_id}")
async def update_category_auth(
    item_id: int,
    category: Category,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())],
    session: Session = Depends(get_session)
):
    if not credentials:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    verify_token(credentials.credentials)
    
    db_category = session.get(Category, item_id)
    if db_category:
        category_data = category.model_dump(exclude={'id'}, exclude_unset=True)
        for key, value in category_data.items():
            setattr(db_category, key, value)
        session.add(db_category)
        session.commit()
        session.refresh(db_category)
        return db_category
    raise HTTPException(status_code=404, detail=f"Category with id {item_id} not found")



@app.delete("/categories/auth/{item_id}")
async def delete_category_auth(
    item_id: int,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())],
    session: Session = Depends(get_session)
):
    if not credentials:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    verify_token(credentials.credentials)
    
    category = session.get(Category, item_id)
    if category:
        session.delete(category)
        session.commit()
        return {"ok": True}
    raise HTTPException(status_code=404, detail=f"Category with id {item_id} not found")



# Subcategories authenticated CRUD
@app.post("/subcategories/auth/add")
async def add_subcategory(
    subcategory: SubCategory,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())],
    session: Session = Depends(get_session)
):
    if not credentials:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    verify_token(credentials.credentials)
    
    try:
        subcategory_data = subcategory.model_dump(exclude={'id'})
        db_subcategory = SubCategory(**subcategory_data)
        session.add(db_subcategory)
        session.commit()
        session.refresh(db_subcategory)
        return {"message": f"SubCategory Added: {db_subcategory.name}", "subcategory": db_subcategory}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating subcategory: {str(e)}")



@app.put("/subcategories/auth/{item_id}")
async def update_subcategory_auth(
    item_id: int,
    subcategory: SubCategory,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())],
    session: Session = Depends(get_session)
):
    if not credentials:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    verify_token(credentials.credentials)
    
    db_subcategory = session.get(SubCategory, item_id)
    if db_subcategory:
        subcategory_data = subcategory.model_dump(exclude={'id'}, exclude_unset=True)
        for key, value in subcategory_data.items():
            setattr(db_subcategory, key, value)
        session.add(db_subcategory)
        session.commit()
        session.refresh(db_subcategory)
        return db_subcategory
    raise HTTPException(status_code=404, detail=f"SubCategory with id {item_id} not found")



@app.delete("/subcategories/auth/{item_id}")
async def delete_subcategory_auth(
    item_id: int,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())],
    session: Session = Depends(get_session)
):
    if not credentials:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    verify_token(credentials.credentials)
    
    subcategory = session.get(SubCategory, item_id)
    if subcategory:
        session.delete(subcategory)
        session.commit()
        return {"ok": True}
    raise HTTPException(status_code=404, detail=f"SubCategory with id {item_id} not found")



# Brands authenticated CRUD
@app.post("/brands/auth/add")
async def add_brand(
    brand: Brand,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())],
    session: Session = Depends(get_session)
):
    if not credentials:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    verify_token(credentials.credentials)
    
    try:
        brand_data = brand.model_dump(exclude={'id'})
        db_brand = Brand(**brand_data)
        session.add(db_brand)
        session.commit()
        session.refresh(db_brand)
        return {"message": f"Brand Added: {db_brand.name}", "brand": db_brand}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating brand: {str(e)}")



@app.put("/brands/auth/{item_id}")
async def update_brand_auth(
    item_id: int,
    brand: Brand,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())],
    session: Session = Depends(get_session)
):
    if not credentials:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    verify_token(credentials.credentials)
    
    db_brand = session.get(Brand, item_id)
    if db_brand:
        brand_data = brand.model_dump(exclude={'id'}, exclude_unset=True)
        for key, value in brand_data.items():
            setattr(db_brand, key, value)
        session.add(db_brand)
        session.commit()
        session.refresh(db_brand)
        return db_brand
    raise HTTPException(status_code=404, detail=f"Brand with id {item_id} not found")



@app.delete("/brands/auth/{item_id}")
async def delete_brand_auth(
    item_id: int,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())],
    session: Session = Depends(get_session)
):
    if not credentials:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    verify_token(credentials.credentials)
    
    brand = session.get(Brand, item_id)
    if brand:
        session.delete(brand)
        session.commit()
        return {"ok": True}
    raise HTTPException(status_code=404, detail=f"Brand with id {item_id} not found")



# Initialize database
@app.on_event("startup")
async def on_startup():
    init_db()

# Run the app
if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)