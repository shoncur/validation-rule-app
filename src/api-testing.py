import requests
from requests.exceptions import HTTPError
import getpass
from base import BASE_URL
import json
import os

url = f'{BASE_URL}/login'
login_headers = {'Content-Type':'application/json'}

def process_initial_release(change_data):
    print('\n\033[34m--Initial Release has been called--\033[0m')
    # Check that each Initial Release item has Files attached
    # Under 'Items Tab Modifications' the 'Item New Phase' should only have the new revision
    # Under 'Items Tab Modifications' the Specs, BOM, Source, Cost, and Files should be checked
    # 'Item View' in documentation

    specs_included = False
    bom_included = False
    source_included = False
    cost_included = False
    files_included = False

    # Get all items in Change
    items_url = f'{co_url}/items'
    items_response = requests.get(items_url, headers=co_headers).json()
    #print(json.dumps(items_response, indent=2))

    initial_release_numbers = []
    not_initial_release_numbers = []
    initial_release_checklist = []

    results_list = items_response.get('results', [])
    for result in results_list:
        affected_item_revision = result.get('affectedItemRevision')
        if affected_item_revision is None:
            initial_release_numbers.append(result.get('newItemRevision')['number'])
            specs = result.get('specsView')['includedInThisChange']
            bom = result.get('bomView')['includedInThisChange']
            sourcing = result.get('sourcingView')['includedInThisChange']
            files = result.get('filesView')['includedInThisChange']
            item_stats = [specs, bom, sourcing, files]
            initial_release_checklist.append(item_stats)
        else:
            not_initial_release_numbers.append(result.get('newItemRevision')['number'])
    print('\033[33mItems that are believed to be initial release: \033[0m')
    for item in initial_release_numbers:
        print(f'\t- {item}')
    print('\033[33mItems that are NOT believed to be initial release: \033[0m')
    for item in not_initial_release_numbers:
        print(f'\t- {item}')

    print('\n\033[33mInitial Release Checklist:\033[0m')

    for i, item in enumerate(initial_release_checklist):
        item_number = initial_release_numbers[i]
        print(f'\t- {item_number}:')

        if item[0] == True:
            print('\t\tSpecs: \033[32m\u2713\033[0m')
        else:
            print('\t\tSpecs: \033[31m\u2717\033[0m')

        if item[1] == True:
            print('\t\tBOM: \033[32m\u2713\033[0m')
        else:
            print('\t\tBOM: \033[31m\u2717\033[0m')

        if item[2] == True:
            print('\t\tSourcing: \033[32m\u2713\033[0m')
        else:
            print('\t\tSourcing: \033[31m\u2717\033[0m')
            
        if item[3] == True:
            print('\t\tFiles: \033[32m\u2713\033[0m')
        else:
            print('\t\tFiles: \033[31m\u2717\033[0m')

def process_document_update(change_data):
    print('\n\033[34m--Document Update has been called--\033[0m')

    # Check that there are redlines included in the files
    file_url = f'{BASE_URL}/changes/{co_guid}/files'
    file_response = requests.get(file_url, headers=co_headers).json()
    #print(json.dumps(file_response, indent=2))

    # Search through all files to get category guid's
    category_ids = [category_id['file']['category']['guid'] for category_id in file_response['results']]
    cat_names = []
    for c in category_ids:
        cat_url = f'{BASE_URL}/settings/files/categories/{c}'
        cat_response = requests.get(cat_url, headers=co_headers).json()
        cat_name = cat_response['name']
        cat_names.append(cat_name)
        #print(json.dumps(cat_response, indent=2))

    if 'Redlines' in cat_names:
        print('\033[32m**This CO has redlines included**\033[0m')
    else:
        print('\033[31m**This CO is missing redlines**\033[0m')
    print('All file categories used in this CO: ')
    for category in cat_names:
        print(f'\t- {category}')

def process_lifecycle_update(change_data):
    print('\n\033[34m--Lifecycle Update has been called--\033[0m')
    # Check that lifecycle has been updated

    items_url = f'{co_url}/items'
    items_response = requests.get(items_url, headers=co_headers).json()
    #print(json.dumps(items_response, indent=2))

    lifecycle_update_numbers = []
    not_lifecycle_update_numbers = []
    list_of_phases = []

    results_list = items_response.get('results', [])
    for result in results_list:
        affected_item_revision = result.get('affectedItemRevision')
        if affected_item_revision is None:
            not_lifecycle_update_numbers.append(result.get('newItemRevision')['number'])
        else:
            lifecycle_update_numbers.append(result.get('newItemRevision')['number'])
            # Get the old lifecycle phase

            # Get the new lifecycle phase
            new_phase = result.get('newLifecyclePhase')['name']
            list_of_phases.append(new_phase)
    
    print('\033[33mItems undergoing lifecycle update (not initial release): \033[0m')
    for i, item in enumerate(lifecycle_update_numbers):
        print(f'\t- {item}')
        print('\t\tPrevious Lifecycle Phase: ')
        print(f'\t\tNew Lifecycle Phase: \033[36m{list_of_phases[i]}\033[0m')

def dispatch_process(type_of_change_value, change_data):
    if type_of_change_value == "Initial Release":
        process_initial_release(change_data)
    elif type_of_change_value == "Document Update":
        process_document_update(change_data)
    elif type_of_change_value == "Lifecycle Update":
        process_lifecycle_update(change_data)
    # Add more conditions as needed
    else:
        print("\n--Unsupported type of change:", type_of_change_value + '--')

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
        #email = input('Enter email: ')
        #password = getpass.getpass('Enter password: ')
        data = {
            'email':f'{email}',
            'password':f'{password}'
        }
        login_response = requests.post(url, headers=login_headers, json=data)
        arena_session_id = login_response.json()['arenaSessionId']
        login_response.raise_for_status()
        login_fail = False

        print(f'\033[32m{login_response}\033[0m')
    except HTTPError as http_error:
        print(f'HTTP error occurred: {http_error}')
    except Exception as error:
        print(f'Invalid entry: {error}')

valid_co = False
while not valid_co:
    try:
        # Searching through Arena to find the specific CO that the user has inputted
        print('\nEnter the 6 digits of the CO you would like to test: ', end='')
        co = 'CO-' + input('\033[35mCO-')
        co_url = f'{BASE_URL}/changes?number={co}'
        co_headers = {'arena_session_id':f'{arena_session_id}', 'Content-Type':'application/json'}
        co_response = requests.get(co_url, headers=co_headers).json()
        #print(co_response, '\n')
        co_guid = co_response['results'][0]['guid']

        # To get more information, we are going to grab the guid that was found and query for it
        co_url = f'{BASE_URL}/changes/{co_guid}'
        co_response = requests.get(co_url, headers=co_headers).json()
        #print(co_response, '\n')

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
            print("\033[31mType of Change not found.\033[0m")

        print()
        valid_co = True
    except HTTPError as http_error:
        print(f'HTTP error occurred: {http_error}')
    except Exception as error:
        print(f'Invalid entry: {error}')

