# coding=UTF-8
import pyproj
#import md5
from gps_update_error import GpsUpdateError
from pyramid.httpexceptions import (
    HTTPOk,
    HTTPBadRequest,
    HTTPForbidden,
    HTTPMethodNotAllowed
    )

from ondestan.services import animal_service
from ondestan.entities.position import Position
from ondestan.config import Config
from ondestan.utils import internal_parse_datetime

import logging

logger = logging.getLogger('ondestan')

legacy_data_header = Config.get_string_value('gps.legacy_data_header')
legacy_beacon_header = Config.get_string_value('gps.legacy_beacon_header')
legacy_positions_divider = Config.get_string_value(
        'gps.legacy_positions_divider')
legacy_params_divider = Config.get_string_value('gps.legacy_params_divider')
legacy_params_positions = Config.get_string_value(
        'gps.legacy_params_positions').split(',')
legacy_default_response = Config.get_string_value(
        'gps.legacy_default_response')
legacy_gps_proj = pyproj.Proj(
        "+init=EPSG:" + Config.get_string_value('gps.legacy_proj'))

data_header = Config.get_string_value('gps.data_header')
positions_divider = Config.get_string_value('gps.positions_divider')
params_divider = Config.get_string_value('gps.params_divider')
header_params_positions = Config.get_string_value(
        'gps.header_params_positions').split(',')
body_params_positions = Config.get_string_value(
        'gps.body_params_positions').split(',')
default_response = Config.get_string_value('gps.default_response')
gps_proj = pyproj.Proj("+init=EPSG:" + Config.get_string_value('gps.proj'))
viewer_proj = pyproj.Proj(
        "+init=EPSG:" + Config.get_string_value('config.viewer_proj'))

base_header_data = {
    'imei': None
}

base_data = {
    'date': None,
    'lat': None,
    'lon': None,
    'battery': None,
    'coverage': None,
    'charging': False
}

legacy_base_data = {
    'imei': None,
    'date': None,
    'lat': None,
    'lon': None,
    'battery': None,
    'coverage': None
}


def get_response_legacy(imei):
    return legacy_default_response


def get_response(imei):
    return default_response


def process_update_request(request):
    if request.method == 'POST':
        try:
            response = process_gps_updates(request)
            return HTTPOk(body_template=response)
        except GpsUpdateError as e:
            logger.error("Gps update couldn't be processed: " + e.msg)
            if e.code == 403:
                return HTTPForbidden(detail=e.msg)
            return HTTPBadRequest(detail=e.msg)
    msg = "Gps update requested with wrong method."
    logger.warning(msg)
    return HTTPMethodNotAllowed(detail=msg)


def process_gps_updates(request):
    if len(request.body) != request.content_length:
        raise GpsUpdateError('Wrong length', 400)
    """if not 'content-md5' in request._headers:
        raise GpsUpdateError('No MD5', 400)
    expected_md5 = request._headers['content-md5']
    if expected_md5 != md5.new(request.params.keys()[0]).hexdigest():
        raise GpsUpdateError('Wrong MD5', 400)"""
    return process_gps_params_base(request.params.keys()[0], request)


def process_gps_params_base(base_params, request):
    logger.debug("Received a GPS update with body: '"
                               + base_params + "'")
    if base_params.startswith(legacy_beacon_header):
        logger.info("Answering OK to beacon data: '"
                       + base_params + "'")
        return
    if base_params.startswith(legacy_data_header):
        return process_gps_params_legacy(base_params, request)
    elif base_params.startswith(data_header):
        return process_gps_params(base_params, request)
    else:
        raise GpsUpdateError('Unaccepted data header', 400)


def process_gps_params(base_params, request):
    base_params = base_params.replace(data_header, '').strip()
    positions = base_params.split(positions_divider)
    header = base_header_data.copy()
    for i in range(0, len(positions)):
        position = positions[i]
        params = position.split(params_divider)
        j = 0
        if i == 0:
            if len(params) > len(header_params_positions):
                logger.info("Received a GPS update with too many"
                               + " inner header params: '"
                               + position + "'")
            if (len(params) < len(header_params_positions)):
                logger.info("Received a GPS update with fewer inner"
                            + " header params than configured: '" + position
                            + "'")
            for key in header_params_positions:
                if j >= len(params):
                    break
                if key in header:
                    header[key] = params[j]
                j += 1
        else:
            data = base_data.copy()
            if len(params) > len(body_params_positions):
                logger.info("Received a GPS update with too many params: '"
                               + position + "'")
            if (len(params) < len(body_params_positions)):
                logger.info("Received a GPS update with fewer params "
                            + "than configured: '" + position + "'")
            for key in body_params_positions:
                if j >= len(params):
                    break
                if key in data:
                    data[key] = params[j]
                j += 1
            process_gps_data(data, header, request)
    return get_response(header['imei'])


def process_gps_data(data, header, request):
    try:
        if header['imei'] == None or header['imei'] == '' or\
        data['date'] == None or data['date'] == '' or data['lon'] == None or\
        data['lon'] == '' or data['lat'] == None or data['lat'] == '' or\
        data['battery'] == None or data['battery'] == '':
            raise GpsUpdateError('Insufficient POST params', 400)
        animal = animal_service.get_animal(header['imei'])
        if animal == None:
            raise GpsUpdateError("No animal matches the passed credentials " +
                                 "(IMEI: '" + header['imei'] + "')", 403)
        no_coverage = False
        if float(data['lon']) == 0.0 and float(data['lat']) == 0.0:
            no_coverage = True
            logger.warning("Received a GPS update with position 0,0")
        position = Position()
        try:
            if (legacy_gps_proj != viewer_proj):
                x, y = pyproj.transform(legacy_gps_proj, viewer_proj,
                    float(data['lon']), float(data['lat']))
            else:
                x, y = float(data['lon']), float(data['lat'])
            position.geom = 'SRID=' + str(position.srid) + ';POINT(' +\
            ('%.12g' % x) + ' ' + ('%.12g' % y) + ')'
        except RuntimeError as e:
            raise GpsUpdateError(e.message, 400)
        position.date = internal_parse_datetime(data['date'])
        if data['battery'] != None:
            position.battery = float(data['battery'])
        if data['coverage'] != None:
            position.coverage = float(data['coverage'])
        if data['charging'] != None:
            position.charging = (int(data['charging']) == 1);
        if no_coverage:
            animal_service.process_no_coverage_position(position, animal,
                                                        request)
        else:
            animal_service.save_new_position(position, animal, request)
    except ValueError as e:
        raise GpsUpdateError(e.message, 400)


def process_gps_params_legacy(base_params, request):
    response = None
    base_params = base_params.replace(legacy_data_header, '').strip()
    positions = base_params.split(legacy_positions_divider)
    for position in positions:
        params = position.split(legacy_params_divider)
        i = 0
        data = legacy_base_data.copy()
        if (len(params) < len(legacy_params_positions)):
            raise GpsUpdateError('Insufficient POST params', 400)
        if len(params) > len(legacy_params_positions):
            logger.warning("Received a GPS update with too many params: '"
                           + position + "'")
        for key in legacy_params_positions:
            if key in data:
                data[key] = params[i]
            i += 1
        if response == None and data['imei'] != None\
            and data['imei'] != '':
            response = get_response_legacy(data['imei'])
        process_gps_data_legacy(data, request)
    return response if response != None else legacy_default_response


def process_gps_data_legacy(data, request):
    try:
        if data['imei'] == None or data['imei'] == '' or data['date'] == None\
        or data['date'] == '' or data['lon'] == None or\
        data['lon'] == '' or data['lat'] == None or\
        data['lat'] == '':
            raise GpsUpdateError('Insufficient POST params', 400)
        animal = animal_service.get_animal(data['imei'])
        if animal == None:
            raise GpsUpdateError("No animal matches the passed credentials " +
                                 "(IMEI: '" + data['imei'] + "')", 403)
        no_coverage = False
        if float(data['lon']) == 0.0 and float(data['lat']) == 0.0:
            no_coverage = True
            logger.warning("Received a GPS update with position 0,0")
        position = Position()
        try:
            if (legacy_gps_proj != viewer_proj):
                x, y = pyproj.transform(legacy_gps_proj, viewer_proj,
                    float(data['lon']), float(data['lat']))
            else:
                x, y = float(data['lon']), float(data['lat'])
            position.geom = 'SRID=' + str(position.srid) + ';POINT(' +\
            ('%.12g' % x) + ' ' + ('%.12g' % y) + ')'
        except RuntimeError as e:
            raise GpsUpdateError(e.message, 400)
        position.date = internal_parse_datetime(data['date'])
        if data['battery'] != None:
            position.battery = float(data['battery'])
        if data['coverage'] != None:
            position.coverage = float(data['coverage'])
        if no_coverage:
            animal_service.process_no_coverage_position(position, animal,
                                                        request)
        else:
            animal_service.save_new_position(position, animal, request)
    except ValueError as e:
        raise GpsUpdateError(e.message, 400)
