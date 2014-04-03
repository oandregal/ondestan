# coding=UTF-8
from sqlalchemy import and_

from ondestan.entities import Animal, Position


def get_all_animals(login=None):
    if login != None:
        return Animal().queryObject().filter(Animal.user.has(login=login)).all()
    else:
        return Animal().queryObject().all()


def get_inactive_animals(login=None):
    if login != None:
        return Animal().queryObject().filter(and_(Animal.user.has(login=login),
                                                Animal.active == False)).all()
    else:
        return Animal().queryObject().filter(Animal.active == False).all()


def get_animal(mac, password):
    if mac != None and password != None:
        return Animal().queryObject().filter(and_(Animal.mac == mac,
                Animal.password == password)).scalar()
    else:
        return None


def get_animal_position_by_date(animal_id, date):
    if animal_id != None and date != None:
        return Position().queryObject().filter(and_(Position.animal_id\
                == animal_id, Position.date == date)).scalar()
    else:
        return None
