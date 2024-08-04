from pydantic import BaseModel, ConfigDict, Field

class UserAuthBase(BaseModel):
    token: str

class UserAuth(UserAuthBase):
    model_config = ConfigDict(from_attributes = True)
    id: int
    user_id: int


class TaskBase(BaseModel):
    title: str

class TaskSharedData(BaseModel):
    owner_id: int    
    is_permite_to_write: bool

class Task(TaskBase):
    model_config = ConfigDict(from_attributes = True)
    id: int
    is_deleted: bool
    owner_id: int
    share_data : TaskSharedData | None = None

class TasksList(BaseModel):
    own_tasks: list[Task]
    shared_tasks: list[Task]


class PermissionBase(BaseModel):
    is_permite_to_write: bool

class Permission(PermissionBase):
    model_config = ConfigDict(from_attributes = True)
    id: int
    is_deleted: bool
    user_id: int
    task_id: int


class UserBase(BaseModel):
    login: str

class UserSign(UserBase):
    password: str

class User(UserBase):
    model_config = ConfigDict(from_attributes = True)
    id: int
    # tasks: list[Task] = []
    # permissions: list[Permission] = []
    
class SuccessAuth(BaseModel):
    user: User
    token: str