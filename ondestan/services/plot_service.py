# coding=UTF-8
from ondestan.entities import Plot


def get_all_plots(login=None):
    if login != None:
        return Plot().queryObject().filter(Plot.user.has(login=login)).all()
    else:
        return Plot().queryObject().all()
