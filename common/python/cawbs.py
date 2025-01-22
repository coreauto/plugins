"""
CoreAuto CaWBS Library
------------------------------------------------
This library provides functions to interact with CoreAuto's REST API for managing
real-time event-based workflows. It includes functions for authentication, retrieving
event payloads, updating step data, and accessing keystore credentials.

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
wbs_iniflag = False
wbs_env = os.environ.get('ENV')  # Environment (e.g., "production", "staging")
wbs_actionid = os.environ.get('ACTIONID')  # Unique action ID for the event
wbs_accesscode = os.environ.get('CA_ACCESS_CODE')  # Access code for API authentication
wbs_url = os.environ.get('CA_WBS_URL')  # Base URL for CoreAuto API
wbs_step = os.environ.get('STEPNAME')  # Name of the current step
wbs_headers = {}  # Request headers for API calls


def Init():
    """
    Initializes the library by authenticating with the CoreAuto API.

    Returns:
        dict: A dictionary with 'status_code' and 'error' (if any).
        - status_code: HTTP response code or custom error code.
        - error: Error message (if applicable).
    """
    global wbs_headers, wbs_iniflag, wbs_url

    # Check for required environment variables
    if not all([wbs_env, wbs_actionid, wbs_accesscode, wbs_url, wbs_step]):
        return {'status_code': 601, 'error': 'Environment variables ENV, ACTIONID, CA_ACCESS_CODE, CA_WBS_URL, STEPNAME should be defined'}

    # Prevent reinitialization
    if wbs_iniflag:
        return {'status_code': 602, 'error': 'init already called'}

    # Prepare API authentication request
    wbs_url = wbs_url.strip('/ ')
    todo = {"apiCode": wbs_accesscode}
    wbs_headers = {"Content-Type": "application/json", "Environment": wbs_env}
    response = requests.post(f"{wbs_url}/v1/auth/apicode", data=json.dumps(todo), headers=wbs_headers)

    # Handle API response
    if response.status_code >= 400:
        try:
            js = response.json()
        except:
            return {'status_code': response.status_code, 'error': 'inaccessible'}
        return {'status_code': response.status_code, 'error': js}

    # Update headers with the authorization token
    js = response.json()
    wbs_headers["Authorization"] = f"Bearer {js['token']}"
    wbs_iniflag = True
    return {'status_code': response.status_code}


def GetEventPayload():
    """
    Retrieves the payload for the current event.

    Returns:
        dict: A dictionary with 'status_code' and 'payload' or 'error'.
    """
    if not wbs_iniflag:
        return {'status_code': 603, 'error': 'Init required'}

    response = requests.get(f"{wbs_url}/v1/rtevent/{wbs_actionid}", headers=wbs_headers)

    if response.status_code >= 400:
        try:
            js = response.json()
        except:
            return {'status_code': response.status_code, 'error': 'inaccessible'}
        return {'status_code': response.status_code, 'error': js}

    js = response.json()
    return {'status_code': response.status_code, 'payload': js["payload"]}


def PutStepPayload(payload):
    """
    Saves the payload for the current step.

    Args:
        payload (dict): Data to be saved.

    Returns:
        dict: A dictionary with 'status_code' or 'error'.
    """
    if not wbs_iniflag:
        return {'status_code': 603, 'error': 'Init required'}

    todo = {"actionId": wbs_actionid, "stepname": wbs_step, "payload": payload}
    response = requests.post(f"{wbs_url}/v1/rtstep/payload", data=json.dumps(todo), headers=wbs_headers)

    if response.status_code >= 400:
        try:
            js = response.json()
        except:
            return {'status_code': response.status_code, 'error': 'inaccessible'}
        return {'status_code': response.status_code, 'error': js}

    return {'status_code': response.status_code}


def GetStepPayload(stepname):
    """
    Retrieves the payload for a specific step.

    Args:
        stepname (str): Name of the step to retrieve payload from.

    Returns:
        dict: A dictionary with 'status_code' and 'payload' or 'error'.
    """
    if not wbs_iniflag:
        return {'status_code': 603, 'error': 'Init required'}

    response = requests.get(f"{wbs_url}/v1/rtstep/payload/{wbs_actionid}/{stepname}", headers=wbs_headers)

    if response.status_code >= 400:
        try:
            js = response.json()
        except:
            return {'status_code': response.status_code, 'error': 'inaccessible'}
        return {'status_code': response.status_code, 'error': js}

    js = response.json()
    return {'status_code': response.status_code, 'payload': js["payload"]}


def GetKeystore(keylist):
    """
    Retrieves sensitive information from the keystore.

    Args:
        keylist (str): Comma-separated list of keys to retrieve.

    Returns:
        dict: A dictionary with 'status_code', 'answer', or 'error'.
    """
    if not wbs_iniflag:
        return {'status_code': 603, 'error': 'Init required'}

    keys = keylist.replace(' ', '')
    response = requests.get(f"{wbs_url}/v1/keystore/{keys}", headers=wbs_headers)

    if response.status_code >= 400:
        try:
            js = response.json()
        except:
            return {'status_code': response.status_code, 'error': 'inaccessible'}
        return {'status_code': response.status_code, 'error': js}

    js = response.json()
    for key in keys.split(','):
        if key not in js:
            return {'status_code': 605, 'error': f"{key} not found"}
    return {'status_code': response.status_code, 'answer': js}
