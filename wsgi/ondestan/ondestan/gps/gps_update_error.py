# coding=UTF-8


class GpsUpdateError(Exception):
    def __init__(self, msg, code):
        self.msg = msg
        self.code = code

    def __str__(self):
        return repr(self.msg)
