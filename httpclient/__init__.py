"""
httpclient

:copyright: (c) 2012 by Franck Cuny
:license: MIT

"""


from http import (
    Request, Response, Headers, Date, Url
)
from http.exception import http_exception
from httpclient.handlers import Handlers
from urllib3.poolmanager import PoolManager
from urllib3 import connectionpool, poolmanager
import os
import time

__title__ = 'httpclient'
__version__ = '0.1'
__author__ = 'Franck Cuny'
__license__ = 'MIT'
__copyright__ = 'Copyright 2012 Franck Cuny'


class HTTPClient(object):

    def __init__(self, agent=None, timeout=10, keep_alive=1,
            default_headers={}, max_redirect=7, with_exceptions=False):

        self.timeout = 60
        self.max_redirect = max_redirect
        self._handlers = Handlers()
        self._with_exceptions = with_exceptions

        if agent is None:
            self.agent = "python-httpclient/{version}".format(
                version=__version__)
        else:
            self.agent = agent

        if len(default_headers) == 0:
            default_headers = [(
                'Connection', 'keep-alive',
            )]

        self._default_headers = Headers(default_headers)

        if 'User-Agent' not in default_headers:
            self._default_headers.add('User-Agent', self.agent)
            self._default_headers.add('User-Agent', 'foooo')

        self._poolmanager = PoolManager(
            maxsize=keep_alive
        )

    def HTTPException(fn):
        def wrapper(*args):
            res = fn(*args)
            if args[0]._with_exceptions:
                if res.is_error:
                    raise http_exception(res)
            return res
        return wrapper

    def add_handler(self, position, cb):
        self._handlers.add_handler(position, cb)

    def remove_handler(self, position):
        self._handler.remove_handler(position)

    def default_header(self, key):
        return self.default_headers.get('key')

    @property
    def default_headers(self):
        return self._default_headers

    @HTTPException
    def request(self, request):
        return self._request(request)

    @HTTPException
    def head(self, url, headers={}):
        request = Request('HEAD', url, headers=headers)
        return self._request(request)

    @HTTPException
    def get(self, url, headers={}):
        request = Request('GET', url, headers=headers)
        return self._request(request)

    @HTTPException
    def put(self, url, headers={}, content=None):
        request = Request('PUT', url, headers=headers, content=content)
        return self._request(request)

    @HTTPException
    def post(self, url, headers={}, content=None):
        request = Request('POST', url, headers=headers, content=content)
        return self._request(request)

    @HTTPException
    def delete(self, url, headers={}, content=None):
        request = Request('DELETE', url, headers=headers)
        return self._request(request)

    @HTTPException
    def mirror(self, url, filename):
        req = Request('GET', url)
        res = self.request(req)
        if res.is_success:
            f = open(filename, 'w')
            f.write(res.content)
            f.close()
            last_modified = Date.time2epoch(res.last_modified)
            if last_modified:
                os.utime(file, (last_modified, last_modified))

    def _request(self, request):

        try:
            resp = self._make_request(request)
        except Exception, e:
            print e
            raise e

        if resp.is_redirect and len(resp.redirects) < self.max_redirect:
            try:
                return self._follow_redirect(resp, request)
            except Exception, e:
                raise e

        return resp

    def _make_request(self, request):

        try:
            request = self._handlers.dispatch('request_prepare', request)
        except Exception, e:
            response = Response(status=400, message='Bad request',
                request=request)
            return response

        url = request.url
        conn = connectionpool.connection_from_url(str(url))

        headers = self._merge_headers(request.headers)

        try:
            dispatch_response = self._handlers.dispatch(
                    'request_send', request)
            if (isinstance(dispatch_response, Response)):
                return dispatch_response
        except Exception, e:
            raise e

        r = conn.urlopen(
            method=request.method,
            url=url.abs_path_query,
            headers=headers,
            timeout=self.timeout,
            body=request.content,
            redirect=False,
        )
        return self._build_response(r, request)

    def _build_response(self, r, request):
        status = r.status
        headers = Headers(r.headers)
        content = r.data

        resp = Response(
            status=status,
            headers=headers,
            content=content,
            message=r.reason,
            request=request
        )

        new_resp = self._handlers.dispatch('response_done', resp)
        if new_resp is not None:
            resp = new_resp

        req = self._handlers.dispatch('response_redirect', resp)

        if req is not None and isinstance(req, Request):
            return self.request(req)

        return resp

    def _merge_headers(self, headers):
        final_headers = Headers(
                self.default_headers.items() + headers.items())
        return final_headers

    def _follow_redirect(self, resp, r):
        redirects = list()
        while (resp.is_redirect and len(redirects) < self.max_redirect):
            location = resp.header('location')
            if location is None:
                break
            redirects.append(resp)
            req = Request(r.method, location)
            resp = self._make_request(req)
            location = resp.header('location')
        resp.redirects = redirects
        return resp
