"""Python Flask API Auth0 integration example
"""

import json
from os import environ as env
from urllib.parse import quote_plus, urlencode

from dotenv import load_dotenv, find_dotenv
from flask import Flask, abort, jsonify, redirect, render_template, session, url_for, request
from authlib.integrations.flask_oauth2 import ResourceProtector
from authlib.integrations.flask_client import OAuth
from token_validator import Auth0JWTBearerTokenValidator
from auth0.authentication import GetToken
from flask_session import Session
from flask_cors import CORS

from user import User
import auth0_service
import signup_validator

# load .env
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

# generate validator with domain and audience
require_auth = ResourceProtector()
validator = Auth0JWTBearerTokenValidator(
    env.get("AUTH0_DOMAIN"),
    env.get("AUTH0_AUDIENCE")
)
require_auth.register_token_validator(validator)

# boot up app
app = Flask(__name__)
CORS(app)
app.secret_key = env.get("APP_SECRET_KEY")

# use Server-side session to make the sesssion size larger
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# generate auth0 client
oauth = OAuth(app)
oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_audience = env.get("AUTH0_AUDIENCE"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)

# home page
@app.route("/")
def home():
    if session.get("user") is not None:
        user_info = json.loads(session.get("user"))
    else:
        user_info = "Empty"

    if session.get("user_log") is not None:
        user_log = json.loads(session.get("user_log"))
    else:
        user_log = "Empty"
    
    return render_template(
        "home.html",
        session = session,
        user_info = user_info,
        user_log = user_log,
        access_token = session.get("token"),
    )

# login callback api
@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = auth0_service.get_api_token()
    user_list = auth0_service.get_all_users_information(token['access_token'])
    session['user'] = json.dumps(user_list, indent=4)
    session['token'] = json.dumps(token, indent=4)
    return redirect("/")

@app.route("/signup")
def signup_page():
    return render_template("signup.html")

@app.route("/signup", methods = ["POST"])
def signup():
    # Extract user signup information from the request
    user = User(request.json)
    result = signup_validator.validate(user)
    if result.get('valid'):
        return auth0_service.send_signup_api(user)
    else:
        abort(400, result.get('text'))

@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://"
        + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

@app.route('/search', methods=['POST'])
def search():
    token = auth0_service.get_api_token()
    firstname = request.form.get('search_firstname')
    lastname = request.form.get('search_lastname')
    state = request.form.get('search_state')
    
    if firstname:
        user_list = auth0_service.search_by_first_name(token['access_token'], firstname)
    elif lastname:
        user_list = auth0_service.search_by_last_name(token['access_token'], lastname)
    elif state:
        user_list = auth0_service.search_by_state(token['access_token'], state)
    else:
        user_list = auth0_service.get_all_users_information(token['access_token'])

    session['user'] = json.dumps(user_list, indent=4)
    session['token'] = json.dumps(token, indent=4)
    return redirect("/")

@app.route("/user/log", methods = ["POST"])
def user_logs():
    token = auth0_service.get_api_token()
    user_id = request.form.get('user_id')
    user_log = auth0_service.get_user_logs(token['access_token'], user_id)
    
    session["user_log"] = json.dumps(user_log, indent=4)
    return redirect("/")

@app.route("/api/private")
@require_auth(None)
def private():
    response = (
        "Your access token was successfully validated!"
        )
    return jsonify(message=response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 3001), debug=True)