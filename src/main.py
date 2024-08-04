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

@app.get("/", summary="Check responsibility")
async def root():
    return {"message": "It's working"}

@app.post("/auth/", response_model=schemas.SuccessAuth, tags=["Auth"], summary="User authorization")
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

@app.get("/task/", response_model=schemas.TasksList, tags=["Task"], summary="[Auth] Get all tasks")
def tasks_list(authed_user: schemas.User = Depends(verify_token), db: Session = Depends(get_db)):
    own_tasks = crud.get_owned_tasks(db=db, owner_id=authed_user.id)
    shared_tasks = crud.get_shared_tasks(db=db, user_id=authed_user.id)
    return schemas.TasksList(
         own_tasks=own_tasks,
         shared_tasks=shared_tasks,
    )

@app.get("/task/{task_id}", response_model=schemas.Task, tags=["Task"], summary="[Auth] Get one task")
def get_task(task_id: int, authed_user: schemas.User = Depends(verify_token), db: Session = Depends(get_db)):
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

@app.post("/task/", response_model=schemas.Task, tags=["Task"], summary="[Auth] Create a new task")
def create_task(task: schemas.TaskBase, authed_user: schemas.User = Depends(verify_token), db: Session = Depends(get_db)):
    return crud.create_task(db=db, task=task, owner_id=authed_user.id)

@app.put("/task/{task_id}", response_model=schemas.Task, tags=["Task"], summary="[Auth] Update a  task")
def update_task(task_id: int, new_task: schemas.TaskBase, authed_user: schemas.User = Depends(verify_token), db: Session = Depends(get_db)):
    db_task = crud.get_task(db=db, task_id=task_id)
    if db_task is None:
        raise HTTPException(
            status_code=400,
            detail="Task not found"
        )
    if db_task.owner_id == authed_user.id:
        crud.update_task(db=db, task=new_task, task_id=db_task.id)
        return crud.get_task(db=db, task_id=task_id)
    task_permission = crud.get_task_permission_for_user(db=db, task_id=task_id, user_id=authed_user.id)
    if task_permission is None or task_permission.is_permite_to_write is False:
        raise HTTPException(
            status_code=400,
            detail="No access to edit task"
        )
    crud.update_task(db=db, task=new_task, task_id=db_task.id)
    return schemas.Task(
        share_data=schemas.TaskSharedData(
            owner_id=db_task.owner_id,
            is_permite_to_write=task_permission.is_permite_to_write
        )
        **crud.get_task(db=db, task_id=task_id)
    )