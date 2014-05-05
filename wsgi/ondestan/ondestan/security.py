# coding=UTF-8
from pyramid.security import (
    effective_principals,
    ACLAllowed,
    has_permission
    )


def get_user_login(request):
    principals = effective_principals(request)
    for principal in principals:
        if type(principal) is unicode:
            return principal
    return None


def check_permission(permission, request):
    permission = has_permission(permission, request.context, request)
    return (type(permission) is ACLAllowed)
