# coding=UTF-8
from ondestan.entities import Plot
from sqlalchemy import and_

import logging

logger = logging.getLogger('ondestan')


def get_all_plots(login=None):
    if login != None:
        return Plot().queryObject().filter(Plot.user.has(login=login)).all()
    else:
        return Plot().queryObject().all()


def create_plot(points, user_id):
    if len(points) < 3:
        logger.error('A plot with less than 3 points cannot be saved...')
        return None
    geom_coordinates = ''
    for point in points:
        geom_coordinates += str(point[0]) + ' ' + str(point[1]) + ','
    geom_coordinates += str(points[0][0]) + ' ' + str(points[0][1])

    plot = Plot()
    plot.user_id = user_id
    plot.geom = 'SRID=' + str(plot.srid) + ';POLYGON((' + geom_coordinates + '))'
    plot.name = 'TEST'
    plot.save()

    return plot


def update_plot_geom(points, plot_id, user_id):
    if len(points) < 3:
        logger.error('A plot with less than 3 points cannot be saved...')
        return None
    geom_coordinates = ''
    for point in points:
        geom_coordinates += str(point[0]) + ' ' + str(point[1]) + ','
    geom_coordinates += str(points[0][0]) + ' ' + str(points[0][1])

    plot = Plot().queryObject().filter(and_(Plot.id == plot_id, Plot.user_id
                                            == user_id)).scalar()
    if plot == None:
        logger.error("Cannot update the non-existent plot with id " + str(plot_id)
                     + " for user id " + str(user_id))
        return None
    plot.geom = 'SRID=' + str(plot.srid) + ';POLYGON((' + geom_coordinates + '))'
    plot.update()

    return plot


def delete_plot(plot_id, user_id):
    plot = Plot().queryObject().filter(and_(Plot.id == plot_id, Plot.user_id
                                            == user_id)).scalar()
    if plot == None:
        logger.error("Cannot delete the non-existent plot with id " + str(plot_id)
                     + " for user id " + str(user_id))
        return False
    plot.delete()

    return True
