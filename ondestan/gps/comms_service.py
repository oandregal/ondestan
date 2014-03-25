# coding=UTF-8
import pyproj
import logging
import md5
from datetime import datetime
from gps_update_error import GpsUpdateError

from ondestan.services import animal_service
from ondestan.entities.position import Position

wgs84=pyproj.Proj("+init=EPSG:4326")
epsg3857=pyproj.Proj("+init=EPSG:3857")
logger = logging.getLogger('ondestan')
date_format = '%Y-%m-%dT%H:%M:%S'

def process_data_updates(request):
    if len(request.body) != request.content_length:
        raise GpsUpdateError('Wrong length')
    if not 'content-md5' in request._headers:
        raise GpsUpdateError('No MD5')
    expected_md5 = request._headers['content-md5']
    if expected_md5 != md5.new(request.body).hexdigest():
        raise GpsUpdateError('Wrong MD5')
    process_data(request.params)


def process_data(params):
    data = base_data.copy()
    if 'mac' in params and 'password' in params and 'date' in params:
        mac = str(params['mac'])
        password = str(params['password'])
        date = datetime.strptime(str(params['date']), date_format)
        battery = float(params['battery'])
        coverage = float(params['coverage'])
        lat = float(params['latitude'])
        lon = float(params['longitude'])
        try:
            x, y = pyproj.transform(wgs84, epsg3857, lon, lat)
        except RuntimeError as e:
            raise GpsUpdateError(e.message)
        logger.info('Processing update for mac: ' + mac +
                ' for date ' + date.strftime(date_format) +
                ' with battery level ' + str(battery) +
                ' with coverage ' + str(coverage) +
                ' at y ' + str(y) +
                ' and x ' + str(x))
        animal = animal_service.get_animal(mac, password)
        if animal == None:
            raise GpsUpdateError("Referenced animal doesn't exist")
        position = Position()
        position.geom = 'SRID=3857;POINT(' + str(x) + ' ' + str(y) + ')'
        position.date = date
        position.battery_level = battery
        position.coverage = coverage
        position.animal_id = animal.id
        position.save()
    elif 'mac[0]' in params and 'password[0]' in params and\
        'date[0]' in params:
        i = 0
        while 'mac[' + str(i) + ']' in params and 'password[' + str(i) + ']' in params and\
        'date[' + str(i) + ']' in params:
            mac = str(params['mac[' + str(i) + ']'])
            password = str(params['password[' + str(i) + ']'])
            date = datetime.strptime(str(params['date[' + str(i) + ']']),
                                     date_format)
            battery = float(params['battery[' + str(i) + ']'])
            coverage = float(params['coverage[' + str(i) + ']'])
            lat = float(params['latitude[' + str(i) + ']'])
            lon = float(params['longitude[' + str(i) + ']'])
            try:
                x, y = pyproj.transform(wgs84, epsg3857, lon, lat)
            except RuntimeError as e:
                raise GpsUpdateError(e.message)
            logger.info('Processing update for mac: ' + mac +
                ' for date ' + date.strftime(date_format) +
                ' with battery level ' + str(battery) +
                ' with coverage ' + str(coverage) +
                ' at y ' + str(y) +
                ' and x ' + str(x))
            animal = animal_service.get_animal(mac, password)
            if animal == None:
                raise GpsUpdateError("Referenced animal doesn't exist")
            position = Position()
            position.geom = 'SRID=3857;POINT(' + str(x) + ' ' + str(y) + ')'
            position.date = date
            position.battery_level = battery
            position.coverage = coverage
            position.animal_id = animal.id
            position.save()
            i += 1
    else:
        raise GpsUpdateError('Insufficient POST params')
