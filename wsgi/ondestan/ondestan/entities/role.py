# coding=UTF-8
from sqlalchemy import Column, Integer, String

from ondestan.entities import Entity
from ondestan.utils import Base


class Role(Entity, Base):

    __tablename__ = "roles"
    _ADMIN_ROLE = 'admin'

    id = Column(Integer, primary_key=True)
    name = Column(String)
