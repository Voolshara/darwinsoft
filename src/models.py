from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.db import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    login = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    tasks = relationship("Task", back_populates="owner")
    authes = relationship("User_Auth", back_populates="user")
    permissions = relationship("Permission", back_populates="user")


class User_Auth(Base):
    __tablename__ = "users_authes"
    
    id = Column(Integer, primary_key=True)
    token = Column(String, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="authes")
    

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    is_deleted = Column(Boolean, default=False)

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="tasks")

    permissions = relationship("Permission", back_populates="task")


class Permission(Base):
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True)
    is_permite_to_write = Column(Boolean) # True - write, False - just for read
    is_deleted = Column(Boolean, default=False)
    
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="permissions")
    
    task_id = Column(Integer, ForeignKey("tasks.id"))
    task = relationship("Task", back_populates="permissions")
    
