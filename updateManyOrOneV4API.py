#update status of a single or multiple integrations

import requests
from requests.auth import HTTPBasicAuth
from urllib.parse import quote


def get_integration_list(oic_instance, username, password, pattern):
    session = requests.Session()
    session.auth = (username, password)
    headers = {
        'Content-Type': 'application/json'
    }
    url = f'https://{oic_instance}/ic/api/integration/v1/integrations?q={{name:/{pattern}/}}'
    response = session.get(url, headers=headers)
    session.close()
    if response.status_code == 200:
        return response.json().get('items', [])
    else:
        print(f"Failed to retrieve integrations: {response.status_code} {response.text}")
        return []


def get_integration_details(oic_instance, username, password, integration_id):
    encoded_integration_id = quote(integration_id, safe='')
    url = f'https://{oic_instance}/ic/api/integration/v1/integrations/{encoded_integration_id}'
    response = requests.get(url, auth=HTTPBasicAuth(username, password))
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve integration {integration_id}: {response.status_code} {response.text}")
        return None


def update_integration_status(oic_instance, username, password, integration_ids, status):
    headers = {
        'Content-Type': 'application/json',
        'X-HTTP-Method-Override': 'PATCH'
    }

    for integration_id in integration_ids:
        integration_details = get_integration_details(oic_instance, username, password, integration_id)
        if integration_details and not integration_details.get('lockedFlag', True):
            encoded_integration_id = quote(integration_id, safe='')
            url = f'https://{oic_instance}/ic/api/integration/v1/integrations/{encoded_integration_id}'

            payload = {
                "status": status
            }

            if status == 'ACTIVATED':
                payload["payloadTracingEnabledFlag"] = True

            response = requests.post(url, headers=headers, json=payload, auth=HTTPBasicAuth(username, password))
            if response.status_code == 200:
                print(
                    f"Integration {integration_id} successfully updated to {status} with payloadTracingEnabledFlag: {payload.get('payloadTracingEnabledFlag', False)}")
            else:
                print(f"Failed to update integration {integration_id}: {response.status_code} {response.text}")
        else:
            print(f"Integration {integration_id} is locked or could not be retrieved.")


# Example usage
oic_instance = 'oic_instance'
username = 'user.name'
password = 'pwd'
pattern = 'REP_'  # Pattern for integration names
status = 'ACTIVATED'  # or 'CONFIGURED'
#status = 'CONFIGURED'

# Determine if we are updating a single integration or multiple integrations
single_integration_id = None  # Set to a specific integration ID to update a single integration | leave as None to update a list of integrations
if single_integration_id:
    integration_ids = [single_integration_id]
else:
    # Retrieve integration list based on pattern
    integration_list = get_integration_list(oic_instance, username, password, pattern)
    integration_ids = [f"{integration['code']}|{integration['version']}" for integration in integration_list]

# Update the status of the integrations
update_integration_status(oic_instance, username, password, integration_ids, status)
