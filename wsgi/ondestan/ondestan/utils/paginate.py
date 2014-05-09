# coding=UTF-8
import urllib


def custom_make_page_url(path, params, page, partial=False, sort=True,
                  get_param='page'):
    params = params.copy()
    params[get_param] = page
    if partial:
        params["partial"] = "1"
    if sort:
        params = params.items()
        params.sort()
    qs = urllib.urlencode(params, True)
    return "%s?%s" % (path, qs)


class Customizable_PageURL_WebOb(object):

    def __init__(self, request, qualified=False, get_param='page'):
        self.request = request
        self.qualified = qualified
        self.get_param = get_param

    def __call__(self, page, partial=False):
        """Generate a URL for the specified page."""
        if self.qualified:
            path = self.request.application_url
        else:
            path = self.request.path
        return custom_make_page_url(path, self.request.GET, page, partial,
                             get_param=self.get_param)
