"""
CoreAuto CaWBSBatch Library
-------------------------------------------
This library provides functions for batch job automation in CoreAuto. It includes
methods for authenticating with the CoreAuto API and securely retrieving credentials
from the keystore.

Repository Information:
- License: https://github.com/coreauto/plugins/blob/main/LICENSE
- Code of Conduct: https://github.com/coreauto/plugins/blob/main/CODE_OF_CONDUCT.md
- Contributing: https://github.com/coreauto/plugins/blob/main/CONTRIBUTING.md
- README: https://github.com/coreauto/plugins/blob/main/README.md
"""

import os
import requests
import json

# Global variables to maintain state
wbs_iniflag = False  # Tracks whether the library has been initialized
wbs_env = os.environ.get('ENV')  # Environment (e.g., "production", "staging")
wbs_accesscode = os.environ.get('CA_ACCESS_CODE')  # API access code
wbs_url = os.environ.get('CA_WBS_URL')  # CoreAuto API base URL
wbs_headers = {}  # Request headers for API calls


def Init():
    """
    Initializes the library by authenticating with the CoreAuto API.

    Returns:
        dict: A dictionary with 'status_code' and 'error' (if any).
        - status_code: HTTP response code or custom error code.
        - error: Error message (if applicable).

    Environment Variables Required:
        - ENV: Specifies the environment (e.g., "production").
        - CA_ACCESS_CODE: API access code for authentication.
        - CA_WBS_URL: Base URL for CoreAuto API.
    """
    global wbs_headers, wbs_iniflag, wbs_url

    # Check if required environment variables are set
    if not all([wbs_env, wbs_accesscode, wbs_url]):
        return {'status_code': 601, 'error': 'Environment variables ENV, CA_ACCESS_CODE, CA_WBS_URL should be defined'}

    # Prevent reinitialization
    if wbs_iniflag:
        return {'status_code': 602, 'error': 'init already called'}

    # Prepare authentication request
    wbs_url = wbs_url.strip('/ ')
    todo = {"apiCode": wbs_accesscode}
    wbs_headers = {"Content-Type": "application/json", "Environment": wbs_env}
    response = requests.post(f"{wbs_url}/v1/auth/apicode", data=json.dumps(todo), headers=wbs_headers)

    # Handle authentication response
    if response.status_code >= 400:
        try:
            js = response.json()
        except:
            return {'status_code': response.status_code, 'error': 'inaccessible'}
        return {'status_code': response.status_code, 'error': js}

    # Set authorization header with the token
    js = response.json()
    wbs_headers["Authorization"] = f"Bearer {js['token']}"
    wbs_iniflag = True
    return {'status_code': response.status_code}


def GetKeystore(keylist):
    """
    Retrieves sensitive credentials or configuration data from the CoreAuto keystore.

    Args:
        keylist (str): A comma-separated list of keys to retrieve.

    Returns:
        dict: A dictionary with 'status_code', 'answer', or 'error'.
        - status_code: HTTP response code or custom error code.
        - answer: Dictionary containing the requested key-value pairs (if successful).
        - error: Error message (if applicable).

    Errors:
        - 603: Init() must be called before this function.
        - 605: One or more requested keys were not found.

    Example Usage:
        response = GetKeystore("db_host,db_user,db_password")
        if response['status_code'] == 200:
            credentials = response['answer']
            print("Keystore retrieved successfully:", credentials)
    """
    if not wbs_iniflag:
        return {'status_code': 603, 'error': 'Init required'}

    # Prepare the API call
    keys = keylist.replace(' ', '')  # Remove unnecessary spaces from the key list
    response = requests.get(f"{wbs_url}/v1/keystore/{keys}", headers=wbs_headers)

    # Handle response
    if response.status_code >= 400:
        try:
            js = response.json()
        except:
            return {'status_code': response.status_code, 'error': 'inaccessible'}
        return {'status_code': response.status_code, 'error': js}

    # Validate returned keys
    js = response.json()
    for key in keys.split(','):
        if key not in js:
            return {'status_code': 605, 'error': f"{key} not found"}

    return {'status_code': response.status_code, 'answer': js}
