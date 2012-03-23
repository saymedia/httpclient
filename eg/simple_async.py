import sys
sys.path.append('.')

from httpclient.async import HTTPClientAsync
from http import Request

ua = HTTPClientAsync()

req = Request('GET', 'http://proximobus.appspot.com/agencies.json')

res = ua.request(req)

if res.is_success:
    print res.content

#try:
    #req = Request('GET', 'http://some.bad.address.that.does.not.exist/')
    #res = ua.request(req)
#except Exception, e:
    #print "OK"
    ##print e
    ##print res.is_error
