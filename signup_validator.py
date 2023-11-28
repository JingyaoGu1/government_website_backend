import re
import pandas as pd

state_db = pd.read_csv("resource/state_abbrev.csv")
state_lst = list(state_db['code']) # list of state abbrev.
us_zipcode = pd.read_csv('resource/us_zipcode.csv') #db showing the record of us zipcode with city, state, etc.

# Init variable
global fieldDict
fieldDict= {'email':True, 'first_name': True, 'middle_name': False, 'last_name': True,
            'ssn': False, 'address_line_1': True, 'address_line_2': False, 'city': True,
            'state': True, 'zipcode': True}

global optionFieldDict
optionFieldDict = {'state':state_lst}

global styleDict
styleDict = {'email':r"^[a-z0-9]*[\._]?[ a-z0-9]+[@]\w+[. ]\w{2,3}$",
            'ssn':r"^\d{3}-\d{2}-\d{4}$",
            'zipcode':r"^\d{5}"} # fix: change email regex + to *

global styleError
styleError = {'email': "Invalid Email Address",
            "zipcode":"Zipcode is 5 digits long (XXXXX)",
            "ssn":"Follow the SSN format: XXX-XX-XXXX"}


def validZip(zipcode, city, state):
    # get input value
    given_zip = int(zipcode)
    given_city = city.lower()
    given_state = state.lower()
    # get a list of true city from database and change to lower case
    true_city = [c.lower() for c in us_zipcode['primary_city']]

    # if input zipcode is not in the true record or input city is not in the true record
    if int(given_zip) not in us_zipcode['zip'].tolist() or given_city not in true_city:
        return False

    else:
        # get the index of zipcode and find the true city and true state in the database accordingly
        zip_index = us_zipcode.index[us_zipcode['zip'] == given_zip][0]
        true_city = us_zipcode['primary_city'][zip_index].lower()
        true_state = us_zipcode['state'][zip_index].lower()
        # return whether input city/state matches the true value
        return given_city == true_city and given_state == true_state


def validate_fields(fields_map):
    # initialize flag
    missing = False
    valid_bool = False

    # Checking:

    # Iterate each input value
    for field in fields_map:
        inputValue = fields_map[field]


        # 1. Mandatory Check (in loop, check every input)
        # If field is mandatory but the value is null, flag missing to be True
        if not inputValue and fieldDict[field]:
            missing = True


        # 2. Style Check (in loop, check every input)
        # For the field has format requirements, check whether the input value match the regex from styleDict
        # If not match, print out error message from styleError dict, flag style_error to be True
        if field in styleDict.keys():
            if not re.match(styleDict[field],inputValue) and inputValue:
                return {'valid': False, 'text': styleError[field]}

    # Out of loop

    # If mandatory field is missing input, print error message
    if missing:
        return {'valid': False, 'text': "Missing Mandatory Information"}

    # If not missing mandatory input and there is no style error
    # Check address validity and assign the bool value to valid_bool
    valid_bool = validZip(fields_map.get('zipcode'), fields_map.get('city'), fields_map.get('state'))

    # If not missing mandatory input but the address is invalid, print error message
    if not valid_bool:
        return {'valid': True, 'text': "Invalid Address"}
    
    return {'valid': True}


def validate(user):
    result = validate_fields(user.fields_map)
    if result.get("text") == "Invalid Address":
        user.address_mismatch = 1
    user.fields_map['address_mismatch'] = str(user.address_mismatch)
    return result