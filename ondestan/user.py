from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .entity import Entity
from .db import Base

class User(Entity, Base):
 
    __tablename__ = "users"
 
    id = Column(Integer, primary_key=True)
    login = Column(String, unique=True)
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    password = Column(String)
    role_id = Column(Integer, ForeignKey("roles.id"))
    role = relationship("Role")
