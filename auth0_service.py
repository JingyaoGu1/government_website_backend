"""Python Flask API Auth0 integration example
"""

import json
import http.client
from os import environ as env
import requests

# send the request to Auth0, get response and loads json
def send_auth0_request(conn):
    res = conn.getresponse()
    data = res.read()
    data = data.decode("utf-8")
    return json.loads(data)

# signup user via Auth0 signup API
def send_signup_api(user):
    meta = user.fields_map
    
    data = {"client_id": env.get("AUTH0_CLIENT_ID"),
            "email": user.email,
            "password": user.password,
            "connection": "Username-Password-Authentication",
            "user_metadata": meta}
    json_data = json.dumps(data)

    headers = { 'Content-type': "application/json" }
    response = requests.post( "https://" + env.get("AUTH0_DOMAIN") + "/dbconnections/signup", data=json_data, headers = headers)
    
    return response.json()

# get access token form API
def get_api_token():
    conn = http.client.HTTPSConnection(env.get("AUTH0_DOMAIN"))
    payload = "{\"client_id\":\"" + env.get("AUTH0_CLIENT_ID") + "\",\"client_secret\":\"" + env.get("AUTH0_CLIENT_SECRET") + "\",\"audience\":\"" + env.get("AUTH0_AUDIENCE") + "\",\"grant_type\":\"client_credentials\"}"
    headers = { 'content-type': "application/json" }
    conn.request("POST", "/oauth/token", payload, headers)
    return send_auth0_request(conn)

# get the information of all users from Auth0 (must has access token)
def get_all_users_information(token):
    conn = http.client.HTTPSConnection(env.get("AUTH0_DOMAIN"))
    headers = { 'authorization': "Bearer " + token}
    conn.request("GET", "/api/v2/users", headers=headers)
    user_meta_data_list = send_auth0_request(conn)
    return user_meta_data_list_to_user_list(user_meta_data_list)

# search
def search_by_first_name(token, firstname):
    conn = http.client.HTTPSConnection(env.get("AUTH0_DOMAIN"))
    headers = { 'authorization': "Bearer " + token}
    conn.request("GET", "/api/v2/users?search_engine=v3&q=user_metadata.first_name:\"" + firstname + "\"", headers=headers)
    user_meta_data_list = send_auth0_request(conn)
    return user_meta_data_list_to_user_list(user_meta_data_list)

def search_by_last_name(token, lastname):
    conn = http.client.HTTPSConnection(env.get("AUTH0_DOMAIN"))
    headers = { 'authorization': "Bearer " + token}
    conn.request("GET", "/api/v2/users?search_engine=v3&q=user_metadata.last_name:\"" + lastname + "\"", headers=headers)
    user_meta_data_list = send_auth0_request(conn)
    return user_meta_data_list_to_user_list(user_meta_data_list)

def search_by_state(token, state):
    conn = http.client.HTTPSConnection(env.get("AUTH0_DOMAIN"))
    headers = { 'authorization': "Bearer " + token}
    conn.request("GET", "/api/v2/users?search_engine=v3&q=user_metadata.state:\"" + state + "\"", headers=headers)
    user_meta_data_list = send_auth0_request(conn)
    return user_meta_data_list_to_user_list(user_meta_data_list)

# get the logs of user from Auth0
def get_user_logs(token, user_id):
    conn = http.client.HTTPSConnection(env.get("AUTH0_DOMAIN"))
    headers = { 'authorization': "Bearer " + token}
    conn.request("GET", "/api/v2/users/" + user_id + "/logs", headers=headers)
    user_logs_list = send_auth0_request(conn)
    return parse_user_log(user_logs_list)


# convert user meta data to user data (retrieve some fields)
def user_meta_data_list_to_user_list(user_meta_data_list):
    user_list = []
    for user_meta_data in user_meta_data_list:
        if "user_metadata" in user_meta_data:
            user = user_meta_data.get("user_metadata").copy()
            user["user_id"] = user_meta_data.get("user_id")
            user["email"] = user_meta_data.get("email")
            user_list.append(user)
    return user_list

# parse user log information (ip, city_name and country_code)
def parse_user_log(user_log):
    return_log = {}
    for log in user_log:
        if "user_name" in log:
            return_log["user_name"] = log.get("user_name")
        if "ip" in log:
            return_log["ip"] = log.get("ip")
        if "location_info" in log:
            location_info = log.get("location_info")
            return_log["city_name"] = location_info.get("city_name")
            return_log["country_code"] = location_info.get("country_code")
    return return_log