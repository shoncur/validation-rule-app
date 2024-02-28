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
    # Documents go from unreleased -> production release      CHECK
    # Always goes to rev A                                    CHECK
    # Everything has checkmarks                               CHECK
    # pdf is the primary file (needs primary file)
    # if RETRAINED then quiz needs to be in implementation

    # Get all items in Change
    items_url = f'{co_url}/items'
    items_response = requests.get(items_url, headers=co_headers).json()
    #print(json.dumps(items_response, indent=2))

    initial_release_numbers = []
    initial_release_sourcing = []
    is_document_list = []
    not_initial_release_numbers = []
    initial_release_checklist = []

    # We need to go to the specific item and check if there is sourcing
    # This needs to change because the check mark is not indicative of there actually being content (ie. specs)

    results_list = items_response.get('results', [])
    for result in results_list:
        affected_item_revision = result.get('affectedItemRevision')
        if affected_item_revision is None:
            item_guid = result.get('newItemRevision')['guid']
            item_number = result.get('newItemRevision')['number']
            lifecycle_phase = result.get('newLifecyclePhase')['name']
            revision = result.get('newRevisionNumber')
            initial_release_numbers.append(item_number)

            # FOR SOURCING----------------------------------------------------
            # search the number in items world
            # NOTE: THAT ALL 'DOCUMENT' TYPES WILL NOT REQUIRE SOURCING
            item_url = f'{BASE_URL}/items/{item_guid}/sourcing'
            item_response = requests.get(item_url, headers=co_headers).json()
            #print(json.dumps(item_response, indent=2))
            sourcing_count = item_response.get('count')

            is_document = False
            sourcing = False

            if sourcing_count == 0:
                # We need to check if it is a document type or not
                # Document type does not need sourcing, other types do not
                
                # Check the prefixes file and see if this item is a document or not
                with open('document_prefixes.txt', 'r') as file:
                    prefixes = [line.strip() for line in file]

                for prefix in prefixes:
                    if item_number.startswith(prefix):
                        is_document = True
                        is_document_list.append(is_document)
                        # If it's a document, we need to make sure that it's going straight to production release
                        break # No need to check the rest of the prefixes if it turns out it's a document

                if is_document:
                    sourcing = True
                    initial_release_sourcing.append(sourcing)
                    if lifecycle_phase != 'Production Release':
                            print('\033[91mInitial release documents must ALWAYS go straight to Production Release\033[0m')
                else:
                    sourcing = False
                    initial_release_sourcing.append(sourcing)
                    is_document_list.append(is_document)

            else:
                sourcing = True
                initial_release_sourcing.append(sourcing)
                is_document_list.append(is_document) # This is only here to ensure that the is_document_list and the other lists line up, if sourcing is there, it does not matter if it is a document or not
                # Maybe we want to fetch the information for the sourcing?
                        
            #----------------------------------------------------------------
            #-----------REVISION----------
            if revision != 'A':
                print('\033[91mAll initial release items must be Rev A\033[0m')
            #-----------------------------
            # Everything must be checkmarked-----------------------------------
            specs_check = result.get('specsView')['includedInThisChange']
            bom_check = result.get('bomView')['includedInThisChange']
            sourcing_check = result.get('sourcingView')['includedInThisChange']
            files_check = result.get('filesView')['includedInThisChange']
            item_check_stats = [specs_check, bom_check, sourcing_check, files_check]
            initial_release_checklist.append(item_check_stats)
            #--------------------------------------------------------------
            #PDF must be the primary file----------------------
            item_url = f'{BASE_URL}/items/{item_guid}/files'
            item_response = requests.get(item_url, headers=co_headers).json()
            #print(json.dumps(item_response, indent=2))

            item_files_count = item_response.get('count')
            if item_files_count == 0:
                print(f'\033[91mThere are no files associated with {item_number}\033[0m')
            else:
                # We need to make sure that there is a primary file
                files_list = item_response.get('results', [])
                has_primary = False
                for file in files_list:
                    primary_status = file.get('primary')
                    file_name = file.get('file')['name']
                    if primary_status:
                        print(f'The primary file is {file_name}')
                        has_primary = True
                        # Check if it is a pdf
                        format_type = file.get('file')['format']
                        if format_type == 'pdf':
                            print('\033[92mPrimary file is a pdf\033[0m')
                        else:
                            print('\033[91mPrimary file should be a pdf (with some exceptions)\033[0m')
                if has_primary == False:
                    print('\033[91mThere is no primary file\033[0m')
                    
            #-------------------------------------------------
        else:
            not_initial_release_numbers.append(result.get('newItemRevision')['number'])

    print('\033[33mItems that are believed to be initial release: \033[0m')
    for i, item in enumerate(initial_release_numbers):
        sourcing = initial_release_sourcing[i]
        is_document = is_document_list[i]

        print(f'\t- {item}')
        print(f'\t\tSourcing status:')

        if is_document and sourcing:
            print(f'\t\t\t\033[92mSourcing included\033[0m')
        if is_document and not sourcing:
            print(f'\t\t\t\033[92mThis item is a document, sourcing is not required\033[0m')
        if not is_document and sourcing:
            print(f'\t\t\t\033[92mSourcing included\033[0m')
        if not is_document and not sourcing:
            print(f'\t\t\t\033[91mThis item is missing sourcing\033[0m')

        print(f'\t\tFile Status:')

    print('\033[33mItems that are NOT believed to be initial release: \033[0m')
    for item in not_initial_release_numbers:
        print(f'\t- {item}')

    print('\n\033[33mModifications Checklist:\033[0m')

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

