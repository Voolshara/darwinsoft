from fastapi import HTTPException

from sqlalchemy.orm import Session
from sqlalchemy import and_

from src import models, schemas
from src.common import get_hashed_password, get_random_hash



def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_login(db: Session, login: str):
    return db.query(models.User).filter(models.User.login == login).first()

def get_user_by_token(db: Session, token: str):
    user_auth =  db.query(models.User_Auth).filter(models.User_Auth.token == token).first()
    if user_auth:
        return user_auth.user
    
def create_user(db: Session, user: schemas.UserSign):
    db_user = models.User(login=user.login, hashed_password=get_hashed_password(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_token(db: Session, user_id: int):
    db_user_auth = models.User_Auth(token=get_random_hash(), user_id=user_id)
    db.add(db_user_auth)
    db.commit()
    db.refresh(db_user_auth)
    return db_user_auth

def get_task(db: Session, task_id: int):
    return db.query(models.Task).filter(and_(
        models.Task.id == task_id,
        models.Task.is_deleted.is_(False)
    )).first()

def get_task_permission_for_user(db: Session, user_id: int, task_id: int):
    return db.query(models.Permission).filter(and_(
        models.Permission.task_id == task_id,
        models.Permission.user_id == user_id,
        models.Permission.is_deleted.is_(False)  
    )).first()

def get_owned_tasks(db: Session, owner_id: int):
    return db.query(models.Task).filter(and_(
            models.Task.owner_id == owner_id, 
            models.Task.is_deleted.is_(False)
        )).all()

def get_shared_tasks(db: Session, user_id: int):
    shared_permissions = db.query(models.Permission).filter(and_(
            models.Permission.user_id == user_id,
            models.Permission.is_deleted.is_(False)
    )).all()
    return [schemas.Task(
        share_data=schemas.TaskSharedData(
            owner_id=i.task.owner_id,
            is_permite_to_write=i.is_permite_to_write
        ),
        **i.task.__dict__
    ) for i in shared_permissions]

def create_task(db: Session, task: schemas.TaskBase, owner_id: int):
    db_task = models.Task(**task.model_dump(), owner_id=owner_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, task_id: int, task: schemas.TaskBase):
    db.query(models.Task).filter(
        models.Task.id == task_id
    ).update({
        models.Task.title: task.title
    })
    db.commit()

def change_task_delete_status(db: Session, task_id: int, delete_status: bool):
    db.query(models.Task).filter(
        models.Task.id == task_id
    ).update({
        models.Task.is_deleted: delete_status
    })
    db.commit()

def get_permisson(db: Session, permisson_id: int):
    return db.query(models.Permission).filter(and_(
        models.Permission.id == permisson_id,
        models.Permission.is_deleted.is_(False)
    )).first()

def create_task_persmission(db: Session, task_id: int, to_user_id: int, permisson: schemas.PermissionBase):
    db_permisson = models.Permission(
        is_permite_to_write = permisson.is_permite_to_write,
        user_id = to_user_id,
        task_id = task_id
    )
    db.add(db_permisson)
    db.commit()
    db.refresh(db_permisson)
    return db_permisson

def update_persmission(db: Session, permisson_id: int, permisson: schemas.PermissionBase):
    db.query(models.Permission).filter(
        models.Permission.id == permisson_id
    ).update({
        models.Permission.is_permite_to_write: permisson.is_permite_to_write
    })
    db.commit()

def change_persmission_delete_status(db: Session, permisson_id: int, delete_status: bool):
    db.query(models.Permission).filter(
        models.Permission.id == permisson_id
    ).update({
        models.Permission.is_deleted: delete_status
    })
    db.commit()
