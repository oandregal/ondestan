from requests import Request, Session
import md5

s = Session()
url = "http://0.0.0.0:6543/gps_update"
params = {'mac': '1', 'password': '1',
          'date': '2014-03-26T19:04:00', 'battery': 80, 'coverage': 80,
          'latitude': 0.000462773316983889, 'longitude': -8.45045187771234e-07}
req = Request('POST', url, data=params)
prepped = req.prepare()
prepped.headers['Content-MD5'] = md5.new(prepped.body).hexdigest()
r = s.send(prepped)
print str(r._content)

params = {'mac[0]': '1', 'mac[1]': '2', 'password[0]': '1',
          'password[1]': '2', 'date[0]': '2014-03-27T19:04:00',
          'date[1]': '2014-03-27T19:04:00', 'battery[0]': 80, 'battery[1]': 15,
          'coverage[0]': 80, 'coverage[1]': 15,
          'latitude[0]': 0.000462773316983889,
          'latitude[1]': 0.000462562123057176,
          'longitude[0]': -8.45045187771234e-07,
          'longitude[1]': -4.88863177617844e-07}
req = Request('POST', url, data=params)
prepped = req.prepare()
prepped.headers['Content-MD5'] = md5.new(prepped.body).hexdigest()
r = s.send(prepped)
print str(r._content)
