from pyramid.security import (
    effective_principals,
    ACLAllowed,
    has_permission
    )
from hashlib import sha512
from .user import User

def group_finder(login, request):
    user = User().queryObject().filter(User.login==login).scalar()
    if ((user != None) and (user.role != None)):
        return ['role:' + user.role.name];
    return [];

def check_login_request(request):
    return check_user_pass(request.params['login'], request.params['password'])

def check_user_pass(login, password):
    user = User().queryObject().filter(User.login==login).scalar()
    if (user != None):
        return user.password == sha512(password).hexdigest()
    return False

def get_user_login(request):
    principals=effective_principals(request)
    for principal in principals:
        if type(principal) is unicode:
            return principal
    return None

def get_user_id(request):
    principals=effective_principals(request)
    for principal in principals:
        if type(principal) is unicode:
            user = User().queryObject().filter(User.login==principal).scalar()
            return user.id
    return None

def check_permission(permission, request):
    return (type(has_permission(permission, request.context, request)) is ACLAllowed)
