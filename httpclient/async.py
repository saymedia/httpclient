from Queue import Queue
from threading import Thread, Event
from httpclient import HTTPClient


## XXX header + set for content
class ResponseAsync(object):
    def __init__(self, callback=None):
        self._response = None
        self._callback = callback
        self._flag = Event()

    def fulfill(self, response):
        self._response = response
        if self._callback is not None:
            self._callback(self)
        self._flag.set()

    def done(self):
        return self._flag.is_set()

    def wait(self):
        self._flag.wait()

    def __getattr__(self, name):
        self.wait()
        return getattr(self._response, name)


class HTTPWorker(Thread):
    def __init__(self, http, handle):
        Thread.__init__(self)
        self._http = http
        self._handle = handle

    def run(self):
        while not self._http._has_work():
            (promise, request) = self._http._get_work()
            response = self._handle.request(request)
            promise.fulfill(response)
        self._http._remove_worker(self)


class HTTPClientAsync(HTTPClient):
    def __init__(self, max_workers=5):
        self.max_workers = max_workers
        self._queue = Queue()
        self._workers = []

    def request(self, request, callback=None):
        if callback is not None:
            promise = callback
        else:
            promise = ResponseAsync()

        self._queue.put((promise, request))
        if len(self._workers) < self.max_workers:
            client = self._get_client()
            worker = HTTPWorker(self, client)
            self._workers.append(worker)
            worker.start()

        return promise

    def _get_client(self):
        client = HTTPClient()
        return client

    def _has_work(self):
        return self._queue.empty()

    def _get_work(self):
        return self._queue.get()

    def _remove_worker(self, worker):
        self._workers.remove(worker)
