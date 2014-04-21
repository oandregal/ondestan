from os import urandom
from itertools import islice, imap, repeat
import string
from config import Config

from pyramid.interfaces import (
    ILocalizer,
    ITranslationDirectories
    )
from pyramid.i18n import (
    get_current_registry,
    make_localizer
    )


def rand_string(length=10):
    chars = set(string.ascii_uppercase + string.ascii_lowercase
                + string.digits)
    char_gen = (c for c in imap(urandom, repeat(1)) if c in chars)
    return ''.join(islice(char_gen, None, length))


def get_custom_localizer(locale):
    if locale == None:
        locale = Config.get_string_value('pyramid.default_locale_name')

    registry = get_current_registry()
    localizer = registry.queryUtility(ILocalizer, name=locale)

    if localizer is None:
        # no localizer utility registered yet
        tdirs = registry.queryUtility(ITranslationDirectories, default=[])
        localizer = make_localizer(locale, tdirs)

        registry.registerUtility(localizer, ILocalizer,
                                 name=locale)
    return localizer
