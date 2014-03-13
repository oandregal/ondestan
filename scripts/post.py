import httplib
import urllib


params = urllib.urlencode({'mac[0]': '11111111'})
headers = {"Content-type": "application/x-www-form-urlencoded",
            "Accept": "text/plain"}
conn = httplib.HTTPConnection("127.0.0.1", 6543)
conn.request("POST", "/gps_update", params, headers)
response = conn.getresponse()
print response.status, response.reason
