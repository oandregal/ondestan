# coding=UTF-8
import pyproj
import logging
import md5
from datetime import datetime
from gps_update_error import GpsUpdateError

from ondestan.services import animal_service
from ondestan.entities.position import Position

wgs84 = pyproj.Proj("+init=EPSG:4326")
epsg3857 = pyproj.Proj("+init=EPSG:3857")
logger = logging.getLogger('ondestan')
date_format = '%Y-%m-%dT%H:%M:%S'

base_data = {
    'imei': None,
    'password': None,
    'date': None,
    'lat': None,
    'lon': None,
    'coverage': None,
    'battery': None
}


def process_gps_updates(request):
    if len(request.body) != request.content_length:
        raise GpsUpdateError('Wrong length', 400)
    if not 'content-md5' in request._headers:
        raise GpsUpdateError('No MD5', 400)
    expected_md5 = request._headers['content-md5']
    if expected_md5 != md5.new(request.params.keys()[0]).hexdigest():
        raise GpsUpdateError('Wrong MD5', 400)
    process_gps_params(request.params.keys()[0])


def process_gps_params(params):
    if 'imei' in params:
        data = base_data.copy()
        for key in params:
            data[key] = params[key]
        process_gps_data(data)
    elif 'imei[0]' in params:
        i = 0
        subfix = '[' + str(i) + ']'
        while 'imei' + subfix in params:
            data = base_data.copy()
            for key in params:
                if key.endswith(subfix):
                    data[key[:-len(subfix)]] = params[key]
            process_gps_data(data)
            i += 1
            subfix = '[' + str(i) + ']'
    else:
        raise GpsUpdateError('Insufficient POST params', 400)


def process_gps_data(data):
    try:
        if data['imei'] == None or data['date'] == None or data['longitude']\
        == None or data['latitude'] == None:
            raise GpsUpdateError('Insufficient POST params', 400)
        animal = animal_service.get_animal(data['imei'])
        if animal == None:
            raise GpsUpdateError("No animal matches the passed credentials " +
                                 "(IMEI: '" + data['imei'] + "')", 403)
        if animal.active:
            process_gps_data_active(data, animal)
        else:
            process_gps_data_inactive(data, animal)
    except ValueError as e:
        raise GpsUpdateError(e.message, 400)


def process_gps_data_active(data, animal):
    try:
        position = Position()
        try:
            x, y = pyproj.transform(wgs84, epsg3857,
                float(data['longitude']), float(data['latitude']))
            position.geom = 'SRID=3857;POINT(' + str(x) + ' ' + str(y) +\
            ')'
        except RuntimeError as e:
            raise GpsUpdateError(e.message, 400)
        position.animal_id = animal.id
        position.date = datetime.strptime(data['date'], date_format)
        if data['battery'] != None:
            position.battery = float(data['battery'])
        if data['coverage'] != None:
            position.coverage = float(data['coverage'])
        if animal_service.get_animal_position_by_date(position.animal_id,
           position.date) == None:
            position.save()
            logger.info('Processed update for IMEI: ' + animal.imei +
                    ' for date ' + position.date.strftime(date_format))
        else:
            logger.warn('Position already exists for animal: ' + str(animal.id)
                    + ' for date ' + position.date.strftime(date_format))
    except ValueError as e:
        raise GpsUpdateError(e.message, 400)


def process_gps_data_inactive(data, animal):
    try:
        logger.info('Processed update for inactive IMEI: ' + animal.imei)
    except ValueError as e:
        raise GpsUpdateError(e.message, 400)