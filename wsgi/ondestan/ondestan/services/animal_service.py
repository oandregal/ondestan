# coding=UTF-8
from pyramid import url
from pyramid.i18n import (
    TranslationString as _
    )
from sqlalchemy import and_

from ondestan.security import check_permission, get_user_email
from ondestan.entities import Animal, Position, Order_state
from ondestan.utils import format_utcdatetime, escape_code_to_eval
from ondestan.utils import internal_format_datetime, get_fancy_time_from_utc
from ondestan.config import Config
import ondestan.services

import logging

logger = logging.getLogger('ondestan')

low_battery_barrier = Config.get_float_value('config.low_battery_barrier')
medium_battery_barrier = Config.get_float_value(
                                'config.medium_battery_barrier')
same_position_max_hours = Config.get_float_value(
                                'config.same_position_max_hours')

# We put these 18n strings here so they're detected when parsing files
_('low_battery_notification_web', domain='Ondestan')
_('low_battery_notification_mail_subject', domain='Ondestan')
_('low_battery_notification_mail_html_body', domain='Ondestan')
_('low_battery_notification_mail_text_body', domain='Ondestan')
_('low_battery_notification_sms', domain='Ondestan')

_('medium_battery_notification_web', domain='Ondestan')

_('gps_immobile_notification_web', domain='Ondestan')
_('gps_immobile_notification_mail_subject', domain='Ondestan')
_('gps_immobile_notification_mail_html_body', domain='Ondestan')
_('gps_immobile_notification_mail_text_body', domain='Ondestan')

_('gps_instant_duplicated_notification_web', domain='Ondestan')

_('gps_inactive_device_notification_web', domain='Ondestan')

_('no_gps_coverage_notification_web', domain='Ondestan')

_('outside_plots_notification_web', domain='Ondestan')
_('outside_plots_notification_mail_subject', domain='Ondestan')
_('outside_plots_notification_mail_html_body', domain='Ondestan')
_('outside_plots_notification_mail_text_body', domain='Ondestan')
_('outside_plots_notification_sms', domain='Ondestan')


def get_all_animals(email=None):
    if email != None:
        return Animal().queryObject().filter(Animal.user.has(email=email)).\
            order_by(Animal.name, Animal.id).all()
    else:
        return Animal().queryObject().order_by(Animal.name, Animal.id).all()


def get_inactive_animals(email=None):
    if email != None:
        return Animal().queryObject().filter(and_(Animal.user.has(email=email),
            Animal.active == False)).order_by(Animal.name, Animal.id).all()
    else:
        return Animal().queryObject().filter(Animal.active == False).\
            order_by(Animal.name, Animal.id).all()


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


def get_animal_by_phone(phone):
    if phone != None:
        return Animal().queryObject().filter(Animal.phone == phone).scalar()
    else:
        return None


def get_animal_position_by_date(animal_id, date):
    if animal_id != None and date != None:
        return Position().queryObject().filter(and_(Position.animal_id\
                == animal_id, Position.date == date)).scalar()
    else:
        return None


def create_animal(imei, phone, order, name=''):
    animal = Animal()
    animal.active = False
    animal.imei = imei
    animal.phone = phone
    if (name != None and name != ''):
        animal.name = name
    if (order != None and order.user != None):
        animal.order_id = order.id
        animal.user_id = order.user.id
        animal.save()


def update_animal_name(animal_id, name, user_id=None):
    if (id != None and name != None):
        if user_id != None:
            animal = Animal().queryObject().filter(and_(Animal.id == animal_id,
                    Animal.user_id == user_id)).scalar()
        else:
            animal = Animal().queryObject().filter(Animal.id ==
                    animal_id).scalar()
        if animal != None:
            animal.name = name
            animal.update()
        else:
            logger.error("Cannot update the non-existent animal with id "
                     + str(animal_id) + " for user id " + str(user_id))


def update_animal_plot(animal_id, plot_id, user_id=None):
    if animal_id != None:
        if user_id != None:
            animal = Animal().queryObject().filter(and_(Animal.id == animal_id,
                    Animal.user_id == user_id)).scalar()
        else:
            animal = Animal().queryObject().filter(Animal.id == animal_id)\
                .scalar()
        if animal != None:
            if plot_id == None or plot_id == '':
                animal.plot_id = None
                animal.update()
            else:
                plot = ondestan.services.plot_service.get_plot_by_id(plot_id)
                if plot != None:
                    if user_id != None:
                        if plot.user_id != user_id:
                            logger.error("Cannot assign the non-existent plot "
                                 + "with id " + str(plot_id)
                                 + " to animal with id "
                                 + str(animal_id) + " for user id "
                                 + str(user_id))
                        return
                    animal.plot_id = plot_id
                    animal.update()
                else:
                    logger.error("Cannot assign the non-existent plot with id "
                         + str(plot_id) + " to animal with id "
                         + str(animal_id) + " for user id " + str(user_id))
        else:
            logger.error("Cannot update the non-existent animal with id "
                         + str(animal_id) + " for user id " + str(user_id))


def delete_animal_by_id(animal_id):
    if animal_id != None:
        animal = Animal().queryObject().filter(Animal.id == animal_id).scalar()
        if animal.n_positions == 0:
            animal.delete()


def activate_animal_by_id(request):
    animal_id = request.matchdict['device_id']
    if check_permission('admin', request):
        email = None
    else:
        email = get_user_email(request)

    if animal_id != None:
        animal = Animal().queryObject().filter(Animal.id == animal_id).scalar()
        if (email != None):
            if (animal.user.email != email):
                return
        animal.active = True
        animal.update()

        same_order_devices = animal.order.devices
        all_active = True
        for device in same_order_devices:
            all_active = all_active and device.active
        if all_active:
            active_order_state = Order_state._STATES[len(Order_state._STATES)
                                                     - 2]
            if device.order.states[0].state != active_order_state:
                ondestan.services.order_service.update_order_state(
                                animal.order.id, active_order_state, request)


def deactivate_animal_by_id(request):
    animal_id = request.matchdict['device_id']
    if check_permission('admin', request):
        email = None
    else:
        email = get_user_email(request)

    if animal_id != None:
        animal = Animal().queryObject().filter(Animal.id == animal_id).scalar()
        if (email != None):
            if (animal.user.email != email):
                return
        animal.active = False
        animal.update()


def save_new_position(position, animal, request):
    if animal.active:
        if get_animal_position_by_date(animal.id, position.date) == None:
            position.animal_id = animal.id
            position.save()
            if animal.positions[0] == position and animal.positions[0].\
                outside() and ((animal.n_positions > 1 and not
                animal.positions[1].outside()) or animal.n_positions == 1):
                parameters = {'name': animal.user.name,
                 'animal_name': animal.name if (animal.name != None and
                                animal.name != '') else animal.imei,
                 'fancy_date': get_fancy_time_from_utc(position.date,
                                locale=animal.user.locale),
                 'fancy_date_eval': escape_code_to_eval(
                    "get_fancy_time_from_utc(internal_parse_datetime('"
                    + internal_format_datetime(position.date)
                    + "'), request=request)"),
                 'date': format_utcdatetime(position.date,
                    locale=animal.user.locale)
                 }
                ondestan.services.\
                notification_service.process_notification(
                    'outside_plots', animal.user.email, True, 3,
                    True, True, parameters)
    process_position_general_notifications(position, animal, request)


def process_no_coverage_position(position, animal, request):
    if animal.active:
        if get_animal_position_by_date(animal.id, position.date) == None:
            parameters = {'name': animal.user.name,
             'animal_name': animal.name if (animal.name != None and
                            animal.name != '') else animal.imei,
             'date': format_utcdatetime(position.date,
                locale=animal.user.locale)
             }
            ondestan.services.\
            notification_service.process_notification(
                'no_gps_coverage', animal.user.email, True, 2,
                False, False, parameters)
    process_position_general_notifications(position, animal, request)


def process_position_general_notifications(position, animal, request):
    if animal.active:
        aux = get_animal_position_by_date(animal.id, position.date)
        if aux == position or aux == None:
            if position.battery != None and\
                position.battery < medium_battery_barrier:
                if position.battery < low_battery_barrier:
                    if animal.positions[0] == position and\
                        (animal.n_positions == 1 or\
                        animal.positions[1].battery >= low_battery_barrier):
                        parameters = {'name': animal.user.name,
                         'animal_name': animal.name if (animal.name != None and
                                        animal.name != '') else animal.imei,
                         'fancy_date': get_fancy_time_from_utc(position.date,
                                        locale=animal.user.locale),
                         'fancy_date_eval': escape_code_to_eval(
                            "get_fancy_time_from_utc(internal_parse_datetime('"
                            + internal_format_datetime(position.date)
                            + "'), request=request)"),
                         'date': format_utcdatetime(position.date,
                            locale=animal.user.locale),
                         'battery_level': position.battery,
                         'url': request.route_url('map')
                         }
                        ondestan.services.\
                        notification_service.process_notification(
                            'low_battery', animal.user.email, True, 3,
                            True, True, parameters)
                else:
                    if animal.positions[0] == position and\
                        (animal.n_positions == 1 or\
                        animal.positions[1].battery >= medium_battery_barrier):
                        parameters = {'name': animal.user.name,
                         'animal_name': animal.name if (animal.name != None and
                                        animal.name != '') else animal.imei,
                         'fancy_date': get_fancy_time_from_utc(position.date,
                                        locale=animal.user.locale),
                         'fancy_date_eval': escape_code_to_eval(
                            "get_fancy_time_from_utc(internal_parse_datetime('"
                            + internal_format_datetime(position.date)
                            + "'), request=request)"),
                         'date': format_utcdatetime(position.date,
                            locale=animal.user.locale),
                         'battery_level': position.battery
                         }
                        ondestan.services.\
                        notification_service.process_notification(
                            'medium_battery', animal.user.email, True, 2,
                            False, False, parameters)
            if animal.n_positions > 1 and animal.positions[0] == position:
                date_end = position.date
                date_begin = date_end
                aux = position
                for pos in animal.positions:
                    if aux.similar_to_position(pos):
                        date_begin = pos.date
                        aux = pos
                    else:
                        break
                delta = date_end - date_begin
                hours_immobile = delta.days * 24 + delta.seconds / 3600.0
                if hours_immobile > same_position_max_hours:
                    first_immobile = True
                    if animal.n_positions > 2:
                        delta_aux = animal.positions[1].date - date_begin
                        hours_immobile_aux = delta_aux.days * 24 +\
                            delta_aux.seconds / 3600.0
                        first_immobile = hours_immobile_aux <=\
                            same_position_max_hours
                    if first_immobile:
                        parameters = {'name': animal.user.name,
                         'animal_name': animal.name if (animal.name != None and
                                        animal.name != '') else animal.imei,
                         'date_begin': format_utcdatetime(date_begin,
                            locale=animal.user.locale),
                         'hours_immobile': int(hours_immobile)
                         }
                        ondestan.services.notification_service.\
                            process_notification('gps_immobile',
                            animal.user.email, True, 2, True,
                            False, parameters)
            logger.info('Processed update for IMEI: ' + animal.imei +
                    ' for date ' + str(position.date))
        else:
            parameters = {'name': animal.user.name,
             'animal_name': animal.name if (animal.name != None and
                            animal.name != '') else animal.imei,
             'date': format_utcdatetime(position.date,
                                        locale=animal.user.locale)
             }
            ondestan.services.notification_service.process_notification(
                'gps_instant_duplicated', animal.user.email, True, 2, False,
                False, parameters)
            logger.warn('Position already exists for animal: ' + str(animal.id)
                + ' for date ' + str(position.date))
    else:
        # This notification is considered rather confusing than useful
        """parameters = {'name': animal.user.name,
         'animal_name': animal.name if (animal.name != None and
                        animal.name != '') else animal.imei,
         'fancy_date': get_fancy_time_from_utc(position.date,
                        locale=animal.user.locale),
         'fancy_date_eval': escape_code_to_eval(
            "get_fancy_time_from_utc(internal_parse_datetime('"
            + internal_format_datetime(position.date)
            + "'), request=request)"),
         'date': format_utcdatetime(position.date, locale=animal.user.locale)
         }
        ondestan.services.notification_service.process_notification(
            'gps_inactive_device', animal.user.email, True, 2, False,
            False, parameters)"""
        logger.warn('Processed update for inactive IMEI: ' + animal.imei +
                    ' for date ' + str(position.date))
