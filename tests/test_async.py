from httpclient.async import ResponseAsync
from http import Response
from unittest2 import TestCase
from datetime import datetime, timedelta
from threading import Thread
from time import sleep


class WaitAndSet(Thread):

    def __init__(self, promise, response, delay):
        Thread.__init__(self)
        self.promise = promise
        self.response = response
        self.delay = delay

    def run(self):
        sleep(self.delay)
        self.promise.fulfill(self.response)


class ResponseTest(TestCase):

    def test_done(self):
        response = ResponseAsync()
        self.assertFalse(response.done(), 'response does not start done')
        std_response = Response(200)
        response.fulfill(std_response)
        self.assertTrue(response.done(), 'response is done after call to fulfill')

    def test_set_and_flag(self):
        response = ResponseAsync()
        self.assertFalse(response.done(), 'response does not start done')
        delay = 0.1
        WaitAndSet(response, Response(200), delay).start()
        start = datetime.now()
        self.assertFalse(response.done(), 'response still not done')
        self.assertEqual(response.status, 200, 'expected status code')
        duration = datetime.now() - start
        min = timedelta(seconds=delay - 0.1)
        max = timedelta(seconds=delay + 0.1)
        self.assertTrue(min < duration and duration < max,
                        'took around 1s to get response and content')
        self.assertTrue(response.done(), 'response now done')

    def test_callback(self):
        def callback(response):
            response.called = True

        response = ResponseAsync(callback)
        response.fulfill(Response(200))
        self.assertEqual(response.status, 200)
        self.assertTrue(response.called)
