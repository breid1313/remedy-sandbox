# Copyright: (c) 2021, Brian Reid
# MIT License
#  
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import requests
import urllib
import os
import json

# mirroring the below curl command with python
# curl -X POST -H 'Content-Type: application/x-www-form-urlencoded' -d 'username=xxxx&password=xxxx' -k  'https://<domain>:<port>/api/jwt/login'

# set just the IP address for remedy as your REMEDY_HOST env var
# I'll take care of the rest
host = os.environ['REMEDY_HOST']
user = os.environ['REMEDY_USER']
password = os.environ['REMEDY_PASSWORD']

# statics
HTTP_PORT = 8008    # server default
HTTPS_PORT = 8443   # server default
HTTP_BASE_URL = "http://" + host + ":" + str(HTTP_PORT) + "/api"
HTTPS_BASE_URL = "https://" + host + ":" + str(HTTPS_PORT) + "/api"

# auth data and headers
data = {"username": user, "password": password}
authHeaders = {"content-type": "application/x-www-form-urlencoded"}

# incident/entry json data
entry = {
    "values": {
        "First_Name": "Allen",
        "Last_Name": "Allbrook",
        "Description": "REST API: Incident Creation",
        "Impact": "1-Extensive/Widespread",
        "Urgency": "1-Critical",
        "Status": "Assigned",
        "Reported Source": "Direct Input",
        "Service_Type": "User Service Restoration",
        "z1D_Action": "CREATE"
    }  
}

print("Testing HTTP API...")
try:
    # set the token url
    url = HTTP_BASE_URL + "/jwt/login"
    # get a token
    # note that this is a byte string
    print("logging in as %s" % user)
    response = requests.request("POST", url, data=data, headers=authHeaders, verify=False)
    if response.status_code == 200:
        print("login successful")
    else:
        print("login failed")
    token = response.content
    # decode the token
    encoding = response.apparent_encoding
    token = token.decode(encoding)
    # add token to request and auth headers
    # authHeaders["Authorization"] = "AR-JWT " + token
    authHeaders["Authorization"] = token
    reqHeaders = {
        "content-type": "application/json",
        # "Authorization": "AR-JWT " + token
        "Authorization": token
    }

    # post the entry
    print("creating a new incident...")
    incident_url = HTTP_BASE_URL + "/arsys/v1/entry/HPD:IncidentInterface_Create?fields=values(Incident Number)"
    response = requests.request("POST", incident_url, json=entry, headers=reqHeaders, verify=False)
    if response.status_code == 201:
        print("successfully created a new incident!")
        # TODO link to incident
        # clear link is not in the response headers or body
        response_json = response.json()
        inc_num = response_json["values"]["Incident Number"]
        print("incident ID: %s" % inc_num)

    # release the token
    # returns 204 no content. this is ok
    print("attemping to log out %s" % user)
    url = HTTP_BASE_URL + "/jwt/logout"
    response = requests.request("POST", url, data=data, headers=authHeaders, verify=False)
    if response.status_code == 204:
        print("Successfully logged out %s" % user)
    else:
        print("Couldnt log out %s" % user)

    # attempt another request once we are logged out
    # this should fail, return 401
    response = requests.request("POST", incident_url, json=entry, headers=reqHeaders, verify=False)
    if response.status_code == 401:
        print("verified that user %s is unable to make API calls post logout" % user)
    else:
        print("user %s was able to create an incident. did the logout request succeed?" % user)
except Exception as e:
    print("ERROR: %s" % e)
print("HTTP API tests complete")

###
# Do the same with HTTPS port
###
"""
TODO
If you run these tests together with the HTTP test above, they will fail.
Your user will fail to get logged in - 401 response with a vague message.
It could be that the user is not getting properly logged out above.
For now, comment out the HTTP tests and just run the HTTPS tests
if you want to use them. They'll work that way.
"""

print("\n\nTesting HTTPS API...")
try:
    # set the token url
    url = HTTPS_BASE_URL + "/jwt/login"
    # get a token
    # note that this is a byte string
    print("logging in as %s" % user)
    response = requests.request("POST", url, data=data, headers=authHeaders, verify=False)
    if response.status_code == 200:
        print("login successful")
    else:
        print("login failed")
    token = response.content
    # decode the token
    encoding = response.apparent_encoding
    token = token.decode(encoding)
    # add token to request and auth headers
    authHeaders["Authorization"] = token
    reqHeaders = {
        "content-type": "application/json",
        # "Authorization": "AR-JWT " + token
        "Authorization": token
    }

    # post the entry
    print("creating a new incident...")
    incident_url = HTTPS_BASE_URL + "/arsys/v1/entry/HPD:IncidentInterface_Create?fields=values(Incident Number)"
    response = requests.request("POST", incident_url, json=entry, headers=reqHeaders, verify=False)
    if response.status_code == 201:
        print("successfully created a new incident!")
        # TODO link to incident
        # clear link is not in the response headers or body
        response_json = response.json()
        inc_num = response_json["values"]["Incident Number"]
        print("incident ID: %s" % inc_num)

    # release the token
    # returns 204 no content. this is ok
    print("attemping to log out %s" % user)
    url = HTTPS_BASE_URL + "/jwt/logout"
    response = requests.request("POST", url, data=data, headers=authHeaders, verify=False)
    if response.status_code == 204:
        print("Successfully logged out %s" % user)
    else:
        print("Couldnt log out %s" % user)

    # attempt another request once we are logged out
    # this should fail, return 401
    response = requests.request("POST", incident_url, json=entry, headers=reqHeaders, verify=False)
    if response.status_code == 401:
        print("verified that user %s is unable to make API calls post logout" % user)
    else:
        print("user %s was able to create an incident. did the logout request succeed?" % user)
except Exception as e:
    print("ERROR: %s" % e)

print("HTTPS API tests complete")
