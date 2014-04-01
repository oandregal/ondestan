# coding=UTF-8
from sqlalchemy import and_

from ondestan.entities import Animal


def get_all_animals(login=None):
    if login != None:
        return Animal().queryObject().filter(Animal.user.has(login=login)).all()
    else:
        return Animal().queryObject().all()


def get_animal(mac, password):
    if mac != None and password != None:
        return Animal().queryObject().filter(and_(Animal.mac == mac,
                Animal.password == password)).scalar()
    else:
        return None
