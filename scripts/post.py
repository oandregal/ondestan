from requests import Request, Session
import httplib
import md5

s = Session()
url = "http://0.0.0.0:6543/gps_update"
params = '1,20141022150735,42.234375,-8.716689,100,2.060000,85'
req = Request('POST', url, data=params)
prepped = req.prepare()
# prepped.headers['Content-MD5'] = md5.new(prepped.body).hexdigest()
r = s.send(prepped)
print str(r._content)

params = '1,20141023150735,0.000462773316983889,-8.45045187771234e-07,100,2.060000,5' + '|||' +\
    '2,20141022150735,0.000462562123057176,-4.88863177617844e-07,100,2.060000,50';
req = Request('POST', url, data=params)
prepped = req.prepare()
# prepped.headers['Content-MD5'] = md5.new(prepped.body).hexdigest()
r = s.send(prepped)
print str(r._content)
