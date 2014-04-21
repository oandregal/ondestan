# coding=UTF-8
from sqlalchemy import and_

from ondestan.security import check_permission, get_user_login
from ondestan.entities import Animal, Position, Order_state
import ondestan.services


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
