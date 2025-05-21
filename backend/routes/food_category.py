from sqlalchemy import select
from fastapi import Depends, APIRouter, HTTPException
from database import models
from typing import List
from database import database
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

# GET: Retrieve all food_category
@router.get("/", response_model=List[models.FoodCategory])
async def get_food_category(db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.FoodCategoryModel))
    food_category = result.scalars().all()
    return food_category

# GET: Retrieve a single food_category by ID
@router.get("/{food_category_id}", response_model=models.FoodCategory)
async def get_food_category(food_category_id: int, db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.FoodCategoryModel).filter(models.FoodCategoryModel.id == food_category_id))
    food_category = result.scalar_one_or_none()
    if food_category is None:
        raise HTTPException(status_code=404, detail="food_category not found")
    return food_category

# POST: Create a new food_category
@router.post("/", response_model=models.FoodCategory)
async def create_food_category(food_category: models.FoodCategory, db: AsyncSession = Depends(database.get_db)):
    db_food_category = models.FoodCategoryModel(**food_category.model_dump(exclude_unset=True))
    db.add(db_food_category)
    print(db_food_category)
    await db.commit()
    await db.refresh(db_food_category)
    return db_food_category

@router.put("/{food_category_id}", response_model=models.FoodCategoryUpdate)
async def update_food_category(food_category_id: int, updated_food_category: models.FoodCategoryUpdate, db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.FoodCategoryModel).filter(models.FoodCategoryModel.id == food_category_id))
    db_food_category = result.scalar_one_or_none()
    if db_food_category is None:
        raise HTTPException(status_code=404, detail="food_category not found")

    # Update directly from model_dump() without calling .food_category()
    for key, value in updated_food_category.model_dump(exclude_unset=True).items():
        setattr(db_food_category, key, value)
    
    await db.commit()
    await db.refresh(db_food_category)
    return db_food_category

@router.patch("/{food_category_id}", response_model=models.FoodCategoryUpdate)
async def patch_food_category(food_category_id: int, food_category_data: models.FoodCategoryUpdate, db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.FoodCategoryModel).filter(models.FoodCategoryModel.id == food_category_id))
    db_food_category = result.scalar_one_or_none()
    if db_food_category is None:
        raise HTTPException(status_code=404, detail="food_category not found")

    for key, value in food_category_data.model_dump(exclude_unset=True).FoodCategory():
        setattr(db_food_category, key, value)
    await db.commit()
    await db.refresh(db_food_category)
    return db_food_category

# DELETE: Delete an food_category by ID
@router.delete("/{food_category_id}")
async def delete_food_category(food_category_id: int, db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.FoodCategoryModel).filter(models.FoodCategoryModel.id == food_category_id))
    db_food_category = result.scalar_one_or_none()
    if db_food_category is None:
        raise HTTPException(status_code=404, detail="food_category not found")
    
    await db.delete(db_food_category)
    await db.commit()
    return {"detail": f"food_category {food_category_id} deleted"}
