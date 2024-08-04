from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from src.common import get_db
from src import crud, models, schemas
from src.db import SessionLocal, engine

models.Base.metadata.create_all(bind=engine) # in real prj use alembic
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "It's working"}

@app.post("/auth/", response_model=schemas.SuccessAuth)
def create_user(user: schemas.UserSign, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_login(db=db, login=user.login)
    if not db_user:
        db_user = crud.create_user(db=db, user=user)
        # raise HTTPException(status_code=400, detail="Пользовтель существует")
    token = crud.create_token(db=db, user_id=db_user.id)
    return schemas.SuccessAuth(
        token=token.token,
        user=db_user
    )
