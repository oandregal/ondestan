# coding=UTF-8
from pyramid.i18n import (
    TranslationString as _
    )
from sqlalchemy import and_

from ondestan.security import check_permission, get_user_login
from ondestan.entities import Animal, Position, Order_state
from ondestan.utils import Config
import ondestan.services

import logging

logger = logging.getLogger('ondestan')

low_battery_barrier = Config.get_float_value('config.low_battery_barrier')
medium_battery_barrier = Config.get_float_value(
                                'config.medium_battery_barrier')

# We put these 18n strings here so they're detected when parsing files
_('low_battery_notification_web', domain='Ondestan')
_('low_battery_notification_mail_subject', domain='Ondestan')
_('low_battery_notification_mail_html_body', domain='Ondestan')
_('low_battery_notification_mail_text_body', domain='Ondestan')

_('medium_battery_notification_web', domain='Ondestan')

_('gps_instant_duplicated_notification_web', domain='Ondestan')

_('gps_inactive_device_notification_web', domain='Ondestan')


def get_all_animals(login=None):
    if login != None:
        return Animal().queryObject().filter(Animal.user.has(login=login)).\
            order_by(Animal.name).all()
    else:
        return Animal().queryObject().order_by(Animal.name).all()


def get_inactive_animals(login=None):
    if login != None:
        return Animal().queryObject().filter(and_(Animal.user.has(login=login),
                                                Animal.active == False)).all()
    else:
        return Animal().queryObject().filter(Animal.active == False).all()


def get_animal(imei):
    if imei != None:
        return Animal().queryObject().filter(Animal.imei == imei).scalar()
    else:
        return None


def get_animal_by_id(animal_id):
    if animal_id != None:
        return Animal().queryObject().filter(Animal.id == animal_id).scalar()
    else:
        return None


def get_animal_by_imei(imei):
    if imei != None:
        return Animal().queryObject().filter(Animal.imei == imei).scalar()
    else:
        return None


def get_animal_position_by_date(animal_id, date):
    if animal_id != None and date != None:
        return Position().queryObject().filter(and_(Position.animal_id\
                == animal_id, Position.date == date)).scalar()
    else:
        return None


def create_animal(imei, order, name=''):
    animal = Animal()
    animal.active = False
    animal.imei = imei
    if (name != None and name != ''):
        animal.name = name
    if (order != None and order.user != None):
        animal.order_id = order.id
        animal.user_id = order.user.id
        animal.save()


def update_animal_name(animal_id, name):
    if (id != None and name != None):
        animal = get_animal_by_id(animal_id)
        if (animal != None):
            animal.name = name
            animal.update()


def delete_animal_by_id(animal_id):
    if animal_id != None:
        animal = Animal().queryObject().filter(Animal.id == animal_id).scalar()
        if (len(animal.positions) == 0):
            animal.delete()


def activate_animal_by_id(request):
    animal_id = request.matchdict['device_id']
    if check_permission('admin', request):
        login = None
    else:
        login = get_user_login(request)

    if animal_id != None:
        animal = Animal().queryObject().filter(Animal.id == animal_id).scalar()
        if (login != None):
            if (animal.user.login != login):
                return
        animal.active = True
        animal.update()

        same_order_animals = animal.order.animals
        all_active = True
        for animal in same_order_animals:
            all_active = all_active and animal.active
        if all_active:
            active_order_state = Order_state._STATES[len(Order_state._STATES)
                                                     - 1]
            if animal.order.states[0].state != active_order_state:
                ondestan.services.order_service.update_order_state(
                                animal.order.id, active_order_state, request)


def deactivate_animal_by_id(request):
    animal_id = request.matchdict['device_id']
    if check_permission('admin', request):
        login = None
    else:
        login = get_user_login(request)

    if animal_id != None:
        animal = Animal().queryObject().filter(Animal.id == animal_id).scalar()
        if (login != None):
            if (animal.user.login != login):
                return
        animal.active = False
        animal.update()


def save_new_position(position, animal):
    if animal.active:
        if get_animal_position_by_date(animal.id, position.date) == None:
            position.animal_id = animal.id
            position.save()
            if position.battery != None and\
                position.battery < medium_battery_barrier:
                if position.battery < low_battery_barrier:
                    if animal.positions[0] == position and (len(animal.positions) == 1 or\
                        animal.positions[1].battery >= low_battery_barrier):
                        parameters = {'name': animal.user.name,
                         'animal_name': animal.name if (animal.name != None and
                                        animal.name != '') else animal.imei,
                         'date': position.date.strftime('%d-%m-%Y %H:%M:%S'),
                         'battery_level': position.battery
                         }
                        ondestan.services.\
                        notification_service.process_notification(
                            'low_battery', animal.user.login, True, 3,
                            True, False, parameters)
                else:
                    if animal.positions[0] == position and (len(animal.positions) == 1 or\
                        animal.positions[1].battery >= medium_battery_barrier):
                        parameters = {'name': animal.user.name,
                         'animal_name': animal.name if (animal.name != None and
                                        animal.name != '') else animal.imei,
                         'date': position.date.strftime('%d-%m-%Y %H:%M:%S'),
                         'battery_level': position.battery
                         }
                        ondestan.services.\
                        notification_service.process_notification(
                            'medium_battery', animal.user.login, True, 2,
                            False, False, parameters)
            logger.info('Processed update for IMEI: ' + animal.imei +
                    ' for date ' + position.date.strftime('%Y-%m-%d %H:%M:%S'))
        else:
            parameters = {'name': animal.user.name,
             'animal_name': animal.name if (animal.name != None and
                            animal.name != '') else animal.imei,
             'date': position.date.strftime('%d-%m-%Y %H:%M:%S')
             }
            ondestan.services.notification_service.process_notification(
                'gps_instant_duplicated', animal.user.login, True, 2, False,
                False, parameters)
            logger.warn('Position already exists for animal: ' + str(animal.id)
                + ' for date ' + position.date.strftime('%Y-%m-%d %H:%M:%S'))
    else:
        parameters = {'name': animal.user.name,
         'animal_name': animal.name if (animal.name != None and
                        animal.name != '') else animal.imei,
         'date': position.date.strftime('%d-%m-%Y %H:%M:%S')
         }
        ondestan.services.notification_service.process_notification(
            'gps_inactive_device', animal.user.login, True, 2, False,
            False, parameters)
        logger.info('Processed update for inactive IMEI: ' + animal.imei +
                    ' for date ' + position.date.strftime('%Y-%m-%d %H:%M:%S'))
