from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy.orm import Session

from src.common import check_password, get_db
from src import crud, models, schemas
from src.db import SessionLocal, engine

models.Base.metadata.create_all(bind=engine) # in real prj use alembic
app = FastAPI()

def verify_token(req: Request):
        if "Authorization" not in req.headers:
            raise HTTPException(
                status_code=401,
                detail="Unauthorized"
            )  
        token = req.headers["Authorization"]
        if token is None:
            raise HTTPException(
                status_code=401,
                detail="Unauthorized"
            )
        return token

@app.get("/")
async def root():
    return {"message": "It's working"}

@app.post("/auth/", response_model=schemas.SuccessAuth)
def create_user(user: schemas.UserSign, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_login(db=db, login=user.login)
    if not db_user:
        db_user = crud.create_user(db=db, user=user)
        # raise HTTPException(status_code=400, detail="Пользовтель существует")
    elif not check_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=400,
            detail="Bad Request"
        )
         
    token = crud.create_token(db=db, user_id=db_user.id)
    return schemas.SuccessAuth(
        token=token.token,
        user=db_user
    )

@app.get("/tasks/", response_model=schemas.TasksList)
def tasks_list(token: bool = Depends(verify_token), db: Session = Depends(get_db)):
    user = crud.get_user_by_token(db=db, token=token)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )
    own_tasks = crud.get_owned_tasks(db=db, owner_id=user.id)
    shared_tasks = crud.get_shared_tasks(db=db, user_id=user.id)
    return schemas.TasksList(
         own_tasks=own_tasks,
         shared_tasks=shared_tasks,
    )
