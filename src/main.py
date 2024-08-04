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
        user = crud.get_user_by_token(db=next(get_db()), token=token)
        if user is None:
            raise HTTPException(
                status_code=401,
                detail="Unauthorized"
            )
        return user

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
def tasks_list(authed_user: schemas.User = Depends(verify_token), db: Session = Depends(get_db)):
    own_tasks = crud.get_owned_tasks(db=db, owner_id=authed_user.id)
    shared_tasks = crud.get_shared_tasks(db=db, user_id=authed_user.id)
    return schemas.TasksList(
         own_tasks=own_tasks,
         shared_tasks=shared_tasks,
    )

@app.get("/task/{task_id}", response_model=schemas.Task)
def tasks_list(task_id: int, authed_user: schemas.User = Depends(verify_token), db: Session = Depends(get_db)):
    task = crud.get_task(db=db, task_id=task_id)
    if task is None:
        raise HTTPException(
            status_code=400,
            detail="Task not found"
        )
    if task.owner_id == authed_user.id:
        return task
    task_permission = crud.get_task_permission_for_user(db=db, task_id=task_id, user_id=authed_user.id)
    if task_permission is None:
        raise HTTPException(
            status_code=400,
            detail="No access to task"
        )
    return schemas.Task(
        share_data=schemas.TaskSharedData(
            owner_id=task.owner_id,
            is_permite_to_write=task_permission.is_permite_to_write
        )
        **task
    )
