# coding=UTF-8
from ..entities.plot import Plot

def get_plot_by_user_login(login):
    Plot().queryObject().filter(Plot.user.has(login=login)).all()

def get_all_plots():
    return Plot().queryObject().all()   