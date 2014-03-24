from requests import Request, Session
import md5

s = Session()
url = "http://0.0.0.0:6543/gps_update"
params = {'mac': '11111111', 'battery': 80}
req = Request('POST', url, data=params)
prepped = req.prepare()
prepped.headers['Content-MD5'] = md5.new(prepped.body).hexdigest() + 'a'
r = s.send(prepped)
print str(r.status_code) + " " + r.reason

params = {'mac[0]': '11111111', 'mac[1]': '22222222',
          'battery[0]': 80, 'battery[1]': 15}
req = Request('POST', url, data=params)
prepped = req.prepare()
prepped.headers['Content-MD5'] = md5.new(prepped.body).hexdigest()
r = s.send(prepped)
print str(r.status_code) + " " + r.reason
