# coding=UTF-8
from ondestan.entities import Cow


def get_all_cows(login=None):
    if login != None:
        return Cow().queryObject().filter(Cow.user.has(login=login)).all()
    else:
        return Cow().queryObject().all()
