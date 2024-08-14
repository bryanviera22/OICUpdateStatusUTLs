#V2 activates integrations with Tracing enabled

import requests
from requests.auth import HTTPBasicAuth
from urllib.parse import quote


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
        # Retrieve integration details
        integration_details = get_integration_details(oic_instance, username, password, integration_id)
        if integration_details and not integration_details.get('lockedFlag', True):
            encoded_integration_id = quote(integration_id, safe='')
            url = f'https://{oic_instance}/ic/api/integration/v1/integrations/{encoded_integration_id}'

            payload = {
                "status": status
            }

            # If activating the integration, also set payloadTracingEnabledFlag to true
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
integration_ids = ['REP_ID001_DELIVE_ATP_ATP|01.00.0000', 'REP_ID002_REVIEW_ATP_ATP|01.00.0000']  # List of integration IDs

#Will delete one after testing
status = 'ACTIVATED'  # or 'CONFIGURED'
#status = 'CONFIGURED'

update_integration_status(oic_instance, username, password, integration_ids, status)
