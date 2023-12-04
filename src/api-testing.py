import requests
from requests.exceptions import HTTPError
import getpass
from base import BASE_URL
import json
import os

url = f'{BASE_URL}/login'
headers = {'Content-Type':'application/json'}

def process_initial_release(change_data):
    # Check that Item Tab has Files attached
    # Under 'Items Tab Modifications' the 'Item New Phase' should only have the new revision
    # Under 'Items Tab Modifications' the Specs, BOM Source Cost and Files should be checked
    print('--Initial Release has been called--')

def process_document_update(change_data):
    # Check that there are redlines included in the files
    print('--Document Update has been called--')
    file_url = f'{BASE_URL}/changes/{co_guid}/files'
    file_response = requests.get(file_url, headers=co_headers).json()
    print(file_response)

def process_lifecycle_update(change_data):
    # Check that lifecycle has been updated
    print('--Lifecycle Update has been called--')

def dispatch_process(type_of_change_value, change_data):
    if type_of_change_value == "Initial Release":
        process_initial_release(change_data)
    elif type_of_change_value == "Document Update":
        process_document_update(change_data)
    elif type_of_change_value == "Lifecycle Update":
        process_lifecycle_update(change_data)
    # Add more conditions as needed
    else:
        print("Unsupported type of change:", type_of_change_value)

# Getting file path for config.json
script_dir = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(script_dir, 'config.json')

# Reading username and pass from config file
with open(config_path, 'r') as file:
    config =json.load(file)

email = config.get('email')
password = config.get('password')

login_fail = True
while login_fail:
    try:
        # email = input('Enter email: ')
        # password = getpass.getpass('Enter password: ')
        data = {
            'email':f'{email}',
            'password':f'{password}'
        }
        login_response = requests.post(url, headers=headers, json=data)
        arena_session_id = login_response.json()['arenaSessionId']
        login_response.raise_for_status()
        login_fail = False

        print(login_response)
    except HTTPError as http_error:
        print(f'HTTP error occurred: {http_error}')
    except Exception as error:
        print(f'Invalid entry: {error}')

valid_co = False
while not valid_co:
    try:
        # Searching through Arena to find the specific CO that the user has inputted
        print('Enter the 6 digits of the CO you would like to test')
        co = 'CO-' + input('CO-')
        co_url = f'{BASE_URL}/changes?number={co}'
        co_headers = {'arena_session_id':f'{arena_session_id}', 'Content-Type':'application/json'}
        co_response = requests.get(co_url, headers=co_headers).json()
        # print(co_response, '\n')
        co_guid = co_response['results'][0]['guid']

        # To get more information, we are going to grab the guid that was found and query for it
        co_url = f'{BASE_URL}/changes/{co_guid}'
        co_response = requests.get(co_url, headers=co_headers).json()

        # Find the 'Type of Change' attribute
        type_of_change_attribute = next(
            (attr for attr in co_response.get('additionalAttributes', []) if attr.get('name') == 'Type of Change'),
            None
        )

        # Extract the value if the attribute is found
        type_of_change_value = type_of_change_attribute.get('value') if type_of_change_attribute else None

        # Perform the dispatch
        if type_of_change_value:
            for type in type_of_change_value:
                dispatch_process(type, data)
        else:
            print("Type of Change not found.")

        valid_co = True
    except HTTPError as http_error:
        print(f'HTTP error occurred: {http_error}')
    except Exception as error:
        print(f'Invalid entry: {error}')

