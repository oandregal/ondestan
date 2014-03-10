# coding=UTF-8
from sqlalchemy import Column, Integer, String

from .entity import Entity
from ..utils.db import Base


class Role(Entity, Base):

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String)
