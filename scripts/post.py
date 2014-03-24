from requests import Request, Session
import md5

s = Session()
url = "http://0.0.0.0:6543/gps_update"
params = {'mac': '11111111', 'password': '123456',
          'date': '2013-05-14T19:04:00', 'battery': 80, 'coverage': 80,
          'latitude': 91.12, 'longitude': 23.23}
req = Request('POST', url, data=params)
prepped = req.prepare()
prepped.headers['Content-MD5'] = md5.new(prepped.body).hexdigest()
r = s.send(prepped)
print str(r.status_code) + " " + r.reason

params = {'mac[0]': '11111111', 'mac[1]': '22222222', 'password[0]': '123456',
          'password[1]': '123456', 'date[0]': '2013-05-14T19:04:00',
          'date[1]': '2013-05-14T19:04:00', 'battery[0]': 80, 'battery[1]': 15,
          'coverage[0]': 80, 'coverage[1]': 15, 'latitude[0]': 91.12,
          'latitude[1]': 23.23, 'longitude[0]': 23.23, 'longitude[1]': 91.12}
req = Request('POST', url, data=params)
prepped = req.prepare()
prepped.headers['Content-MD5'] = md5.new(prepped.body).hexdigest()
r = s.send(prepped)
print str(r.status_code) + " " + r.reason
