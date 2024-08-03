from pydantic import BaseModel

class User(BaseModel):
    id: int | None 
    login: str
    password: str
    
class Task(BaseModel):
    id: int | None
    user_id : int
    title: str
    is_deleted: bool

class Permission(BaseModel):
    id: int | None
    user_id: int
    task_id: int
    is_permite_to_write: bool # True - write, False - just for read
    is_deleted: bool
