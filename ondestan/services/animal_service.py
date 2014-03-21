# coding=UTF-8
from ondestan.entities import Animal


def get_all_animals(login=None):
    if login != None:
        return Animal().queryObject().filter(Animal.user.has(login=login)).all()
    else:
        return Animal().queryObject().all()
