# coding=UTF-8
from ondestan.entities import Cow


def get_cow_by_user_login(login):
    Cow().queryObject().filter(Cow.user.has(login=login)).all()


def get_all_cows():
    return Cow().queryObject().all()
