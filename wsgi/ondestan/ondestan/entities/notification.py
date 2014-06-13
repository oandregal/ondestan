# coding=UTF-8
from pyramid.i18n import (
    get_localizer,
    TranslationString as _
    )

from sqlalchemy import Column, Integer, ForeignKey, String, Date, Boolean
from sqlalchemy.orm import relationship, backref

from ondestan.entities import Entity
from ondestan.utils import *
import logging
from datetime import datetime

logger = logging.getLogger('ondestan')

# We put these 18n strings here so they're detected when parsing files
_('web', domain='Ondestan')
_('sms', domain='Ondestan')
_('e-mail', domain='Ondestan')

_('success', domain='Ondestan')
_('info', domain='Ondestan')
_('warning', domain='Ondestan')
_('danger', domain='Ondestan')


class Notification(Entity, Base):

    __tablename__ = "notifications"
    _LEVELS = ['success', 'info', 'warning', 'danger']
    _TYPES = ['web', 'e-mail', 'sms']

    id = Column(Integer, primary_key=True)
    text = Column(String)
    level = Column(Integer)
    type = Column(Integer)
    date = Column(Date)
    archived = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", backref=backref('notifications',
                                                  order_by=date.desc()))

    def get_full_html(self, request=None):
        # If the request is passed, then we can try to translate the message
        if request != None:
            text = self.get_translated_text(request)
        else:
            text = self.text
        if self.level == None or self.level < 0 or\
           self.level >= len(self._LEVELS):
            logger.error("Invalid notification level: " + self.level)
            level = self._LEVELS[0]
        else:
            level = self._LEVELS[self.level]
        return HtmlContainer('<div class="alert alert-' + level +
            ' alert-dismissable"><button type="button" class="close" \
            data-dismiss="alert" aria-hidden="true">&times;</button>' +
            text + '</div>')

    def get_simple_html(self, request=None):
        # If the request is passed, then we can try to translate the message
        if request != None:
            text = self.get_translated_text(request)
        else:
            text = self.text
        return HtmlContainer(text)

    def get_translated_text(self, request):
        try:
            localizer = get_localizer(request)
            return localizer.translate(eval(unescape_code_to_eval(self.text)))
        except:
            logger.error("Couldn't eval content of notification:'" +
                        self.text + "'")
            return self.text

    def get_type_as_text(self, request):
        if self.type == None:
            return ''
        if self.type < 0 or self.type >= len(Notification._TYPES):
            logger.error("Invalid notification type cannot be " +
                        "translated to text:'" + self.type + "'")
            return self.type
        localizer = get_localizer(request)
        return localizer.translate(_(Notification._TYPES[self.type],
                                     domain='Ondestan'))

    def get_level_as_text(self, request):
        if self.level == None:
            return ''
        if self.level < 0 or self.level >= len(self._LEVELS):
            logger.error("Invalid notification level: " + self.level)
            return self.level
        localizer = get_localizer(request)
        return localizer.translate(_(Notification._LEVELS[self.level],
                                     domain='Ondestan'))
