from database import models, database
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import food
from routes import food_category

app = FastAPI()

app.include_router(food.router, prefix="/food", tags=["Foods"])
app.include_router(food_category.router, prefix="/food_category", tags=["FoodsCategories"])

# Allow all origins (for development purposes only)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow any origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow any method (GET, POST, etc.)
    allow_headers=["*"],  # Allow any headers
)

# Create the tables
@app.on_event("startup")
async def on_startup():
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

# Root Message
@app.get("/")
async def root():
    return {"message": "Service is walking"}
