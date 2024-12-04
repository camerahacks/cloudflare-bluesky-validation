import json
import requests as rq
import os
import sys

############
# SETTINGS
############

CLOUDFLARE_ACCOUNT_ID = os.environ["CLOUDFLARE_ACCOUNT_ID"]
CLOUDFLARE_API_TOKEN = os.environ["CLOUDFLARE_API_TOKEN"]

API_BASE_URL = 'https://api.cloudflare.com/client/v4/accounts/' + CLOUDFLARE_ACCOUNT_ID

############
# HELPER METHODS
############

def load_settings():
    
    # Open the settings file if one exists
    if(os.path.exists('settings.json')):
        
        with open('settings.json') as settings_file:
        
            settings = json.load(settings_file)

    else:

        settings = {}

    return settings

def get_headers():

    headers = {
        'Authorization': 'Bearer ' + CLOUDFLARE_API_TOKEN,
        'Content-Type': 'application/json'
    }

    return headers

def send_api_request(method, endpoint, params=[], body=''):

    req = rq.request(method=method, url=endpoint, headers=get_headers(), json=body)

    return req.json()

############
# CLOUDFLARE API METHODS
############

def get_dbs():

    endpoint = API_BASE_URL + '/d1/database'

    http_method = 'GET'

    result = send_api_request(http_method, endpoint)

    return result['result']
    
def create_db(db):
    pass

def create_table(table):
    pass

def query_db(query, db):

    endpoint = API_BASE_URL + '/d1/database/' + db + '/query'

    method = 'POST'

    result = send_api_request(method=method, endpoint=endpoint, body=query)

    return result['result']

def save_settings(settings):
    with open('settings.json', 'w') as settings_file:
         json.dump(settings, settings_file)

    pass

############
# METHODS
############

def list_dbs(dbs):
    
    if len(dbs) == 0:

        print('No DBs found for this account')

    else:
        print('\nAvailable DBs')
        for db in dbs:
            
            print('Name: ' + db['name'] + ' uuid: '+ db['uuid'] + ' Created at: ' + db['created_at'] + ' Num tables: ' + str(db['num_tables']))

def list_tables(tbls):
    
    if len(tbls) == 0:

        print('No Tables found in this DB')

    else:
        print('\nAvailable Tables')
        for tbl in tbls:
            
            print('Name: ' + tbl['tbl_name'] )

def list_handles(hdls):
    
    if len(hdls) == 0:

        print('No Handles found in this Table')

    else:
        print('\nAvailable Handles')
        for hdl in hdls:
            
            print('Handle: ' + hdl['handle'] + ' DID: ' + hdl['did'] )

def show_db_selection(db_options):

    print('\nD1 Databases:')
    for n, value in db_options.items():
            print(f"{n}. {value['name']} {value['uuid']}")

def show_table_selection(tb_options):
    print('\nD1 Tables:')
    for n, value in tb_options.items():
            print(f"{n}. {value['tbl_name']}")

def get_tables():

    query = {}
    query['sql'] = 'SELECT "tbl_name" FROM sqlite_master WHERE type="table";'

    result = query_db(query, settings['db']['uuid'])

    return result

def get_handles(db, table):

    query = {}
    query['sql'] = 'SELECT * FROM ' + table + ';'

    result = query_db(query, db)

    return result

def add_handle(handle, did):

    query = {}
    query['sql'] = 'INSERT INTO ' + settings['table']['tbl_name'] + '(handle, did) VALUES (?, ?)'
    query['params'] = [handle, did]

    result = query_db(query, settings['db']['uuid'])

    return result

def delete_handle(handle):

    query = {}
    query['sql'] = 'DELETE FROM ' + settings['table']['tbl_name'] + ' WHERE handle = ?'
    query['params'] = [handle]

    result = query_db(query, settings['db']['uuid'])

    return result

options = {
            "1":"List DBs",
            "2":"Select DB",
            "3":"Create DB",
            "4":"List Tables",
            "5":"Select Table",
            "6":"Create Table",
            "6":"List Handles",
            "7":"Add Handle",
            "8":"Delete Handle",
            "9":"Quit"
            }

def show_options():
    print('')
    for c, desc in options.items():
        print(f"{c}. {desc}")

def select_db():

    dbs = get_dbs()
    if len(dbs) == 0:
        print('')
        print('Create a DB First')

        return 0
    
    db_options = {}
    for index, value in enumerate(dbs):
        db_options[str(index+1)] = value
    
    show_db_selection(db_options=db_options)

    choice = input("Select DB (0 to Go Back): ")
    if ( choice == '0'):
            return 0

    while choice not in db_options:
        show_db_selection(db_options)
        choice = input(f"\nChoose one of the options above (0 to Go Back): ")
        if ( choice == '0'):
            return 0

    return db_options[choice]

def select_table():

    tbls = get_tables()
    if len(tbls) == 0:
        print('')
        print('Create a Table First')

        return 0
    
    tb_options = {}
    for index, value in enumerate(tbls[0]['results']):
        tb_options[str(index+1)] = value
    
    print(tb_options)
    show_table_selection(tb_options=tb_options)

    choice = input("Select DB (0 to Go Back): ")
    if ( choice == '0'):
            return 0

    while choice not in tb_options:
        show_table_selection(tb_options)
        choice = input(f"\nChoose one of the options above (0 to Go Back): ")
        if ( choice == '0'):
            return 0

    return tb_options[choice]

while True:

    settings = load_settings()
    print("\nCloudFlare Worker BlueSky Handle Manager")
    if 'db' in settings:
        print('\nUsing DB: ' + settings['db']['name'])

    if 'table' in settings:
        print('Using Table: ' + settings['table']['tbl_name'])

    

    # Show the option selection menu
    show_options()

    choice = ''

    choice = input("Select Option: ")
    while choice not in options:
        show_options()
        choice = input(f"Choose one of options: {', '.join(options)}: ")

    # List DBs
    if choice == "1":
        
        print('')
        dbs = get_dbs()
        list_dbs(dbs)

    # Select DB
    if choice == "2":
        
        db_choice = select_db()
        if( db_choice == 0 ):
            continue

        # save the selected DB in the settings file
        settings['db'] = db_choice

        save_settings(settings)

    # List Tables
    if choice == "4":
        if not 'db' in settings:
            print("\nPlease Select or Create a DB First")
            continue

        tables = get_tables()
        # print(tables)

        list_tables(tables[0]['results'])

    # Select Table
    if choice == "5":
        if not 'db' in settings:
            print("\nPlease Select or Create a DB First")
            continue
        
        tbl_choice = select_table()
        if( tbl_choice == 0 ):
            continue

        # save the selected table in the settings file
        settings['table'] = tbl_choice

        save_settings(settings)
        
    # List Handles
    if choice == "6":
        if not 'db' in settings:

            print("\nPlease Select or Create a DB First")
            continue

        elif not 'table' in settings:

            print("\nPlease Select or Create a Table First")
            continue
        
        else:
            handles = get_handles(settings['db']['uuid'], settings['table']['tbl_name'])
            list_handles(handles[0]['results'])

    # Add Handle
    if choice == "7":
        if not 'db' in settings:

            print("\nPlease Select or Create a DB First")
            continue

        elif not 'table' in settings:

            print("\nPlease Select or Create a Table First")
            continue

        else:
            handle = input("Handle: ")
            did = input("DID: ")

            # Add confirmation before adding info to DB

            result = add_handle(handle, did)

            if( ( result[0]['success'] == True ) & ( result[0]['meta']['rows_written'] != 0 ) ):
                print("Handle added to DB")
            
            else:
                print("An error occurred. Handle not added to DB")


    # Delete Handle
    if choice == "8":
        if not 'db' in settings:

            print("\nPlease Select or Create a DB First")
            continue

        elif not 'table' in settings:

            print("\nPlease Select or Create a Table First")
            continue

        else:
            handle = input("Handle to delete: ")

            # Add confirmation before adding info to DB

            result = delete_handle(handle)

            if((result[0]['success'] == True) & (result[0]['meta']['rows_written'] != 0)):
                print("Handle deleted from the DB")
            
            elif ((result[0]['success'] == True) & (result[0]['meta']['rows_written'] == 0)):
                print("No rows changed. Most likely, handle does not exits")

            else:
                print("An error occurred. Handle was not deleted")

    elif choice == "9":
        print('')
        print("Quitting...")
        break


