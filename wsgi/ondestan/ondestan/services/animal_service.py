# coding=UTF-8
from sqlalchemy import and_

from ondestan.entities import Animal, Position


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


def activate_animal_by_id(animal_id, login=None):
    if animal_id != None:
        animal = Animal().queryObject().filter(Animal.id == animal_id).scalar()
        if (login != None):
            if (animal.user.login != login):
                return
        animal.active = True
        animal.update()


def deactivate_animal_by_id(animal_id, login=None):
    if animal_id != None:
        animal = Animal().queryObject().filter(Animal.id == animal_id).scalar()
        if (login != None):
            if (animal.user.login != login):
                return
        animal.active = False
        animal.update()
