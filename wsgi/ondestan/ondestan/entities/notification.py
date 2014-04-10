# coding=UTF-8
from pyramid.i18n import (
    get_localizer,
    TranslationString as _
    )

from sqlalchemy import Column, Integer, ForeignKey, String, Date, Boolean
from sqlalchemy.orm import relationship, backref

from ondestan.entities import Entity
from ondestan.utils import Base, HtmlContainer
import logging

logger = logging.getLogger('ondestan')


class Notification(Entity, Base):

    __tablename__ = "notifications"
    _LEVELS = ['success', 'info', 'warning', 'danger']

    id = Column(Integer, primary_key=True)
    text = Column(String)
    level = Column(Integer)
    date = Column(Date)
    archived = Column(Boolean)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", backref=backref('notifications',
                                                  order_by=date.desc()))

    def get_html(self, request=None):
        # If the request is passed, then we can try to translate the message
        if request != None:
            try:
                localizer = get_localizer(request)
                text = localizer.translate(eval(self.text))
            except:
                logger.warn("Couldn't eval content of notification:'" +
                            self.text + "'")
                text = self.text
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
