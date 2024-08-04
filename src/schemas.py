from pydantic import BaseModel

class UserAuthBase(BaseModel):
    token = str

class UserAuth(UserAuthBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


class TaskBase(BaseModel):
    title = str

class Task(TaskBase):
    id: int
    is_deleted: bool
    owner_id: int

    class Config:
        orm_mode = True

class PermissionBase(BaseModel):
    is_permite_to_write: bool

class Permission(PermissionBase):
    id: int
    is_deleted: bool
    user_id: int
    task_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str

class UserSign(UserBase):
    password: str

class User(UserBase):
    id: int
    tasks: list[Task] = []
    authes: list[UserAuth] = []
    permissions: list[Permission] = []

    class Config:
        orm_mode = True

    