from fastapi import FastAPI
from src import crud, models, schemas
from src.db import SessionLocal, engine

models.Base.metadata.create_all(bind=engine) # in real prj use alembic
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "It's working"}

@app.get("/users/me")
async def read_user_me():
    return {"user_id": "the current user"}


@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}