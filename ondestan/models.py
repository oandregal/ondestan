# coding=UTF-8
from pyramid.security import (
    Allow,
    Everyone,
    Authenticated
    )

class RootFactory(object):
    __acl__ = [ (Allow, Everyone, 'guest'),
                (Allow, Authenticated, 'view'),
                (Allow, 'role:manager', 'edit'),
                (Allow, 'role:admin', 'edit'),
                (Allow, 'role:admin', 'admin') ]
    def __init__(self, request):
        pass
