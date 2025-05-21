from sqlalchemy import select
from fastapi import Depends, APIRouter, HTTPException
from database import models
from typing import List
from database import database
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

# GET: Retrieve all food
@router.get("/", response_model=List[models.Food])
async def get_food(db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.FoodModel))
    food = result.scalars().all()
    return food

# GET: Retrieve a single food by ID
@router.get("/{food_id}", response_model=models.Food)
async def get_food(food_id: int, db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.FoodModel).filter(models.FoodModel.id == food_id))
    food = result.scalar_one_or_none()
    if food is None:
        raise HTTPException(status_code=404, detail="food not found")
    return food

# POST: Create a new food
@router.post("/", response_model=models.Food)
async def create_food(food: models.Food, db: AsyncSession = Depends(database.get_db)):
    db_food = models.FoodModel(**food.model_dump(exclude_unset=True))
    db.add(db_food)
    print(db_food)
    await db.commit()
    await db.refresh(db_food)
    return db_food

@router.put("/{food_id}", response_model=models.FoodUpdate)
async def update_food(food_id: int, updated_food: models.FoodUpdate, db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.FoodModel).filter(models.FoodModel.id == food_id))
    db_food = result.scalar_one_or_none()
    if db_food is None:
        raise HTTPException(status_code=404, detail="food not found")

    # Update directly from model_dump() without calling .food()
    for key, value in updated_food.model_dump(exclude_unset=True).items():
        setattr(db_food, key, value)
    
    await db.commit()
    await db.refresh(db_food)
    return db_food

@router.patch("/{food_id}", response_model=models.FoodUpdate)
async def patch_food(food_id: int, food_data: models.FoodUpdate, db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.FoodModel).filter(models.FoodModel.id == food_id))
    db_food = result.scalar_one_or_none()
    if db_food is None:
        raise HTTPException(status_code=404, detail="food not found")

    for key, value in food_data.model_dump(exclude_unset=True).food():
        setattr(db_food, key, value)
    await db.commit()
    await db.refresh(db_food)
    return db_food

# DELETE: Delete an food by ID
@router.delete("/{food_id}")
async def delete_food(food_id: int, db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.FoodModel).filter(models.FoodModel.id == food_id))
    db_food = result.scalar_one_or_none()
    if db_food is None:
        raise HTTPException(status_code=404, detail="food not found")
    
    await db.delete(db_food)
    await db.commit()
    return {"detail": f"food {food_id} deleted"}
