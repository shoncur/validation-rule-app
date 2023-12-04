import requests
from requests.exceptions import HTTPError
import getpass
from base import BASE_URL

url = f'{BASE_URL}/login'
headers = {'Content-Type':'application/json'}

login_fail = True
while login_fail:
    try:
        email = input('Enter email: ')
        password = getpass.getpass('Enter password: ')
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
        print('Enter the 6 digits of the CO you would like to test')
        co = 'CO-' + input('CO-')
        co_url = f'{BASE_URL}/changes?number={co}'
        co_headers = {'arena_session_id':f'{arena_session_id}', 'Content-Type':'application/json'}
        co_response = requests.get(co_url, headers=co_headers).json()

        print(co_response)
    except HTTPError as http_error:
        print(f'HTTP error occurred: {http_error}')
    except Exception as error:
        print(f'Invalid entry: {error}')