# coding=UTF-8
from pyramid.security import (
    effective_principals,
    ACLAllowed,
    has_permission
    )
from .services import user_service

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
            user = user_service.get_user_by_login(principal)
            return user.id
    return None

def check_permission(permission, request):
    return (type(has_permission(permission, request.context, request)) is ACLAllowed)
