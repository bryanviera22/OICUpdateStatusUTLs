# Fixed issue where script updates unexpected integrations
# issue is due to script looking for the pattern anywhere in the name and not just at the beginning of int name

from flask import Flask, request, render_template
import requests
from requests.auth import HTTPBasicAuth
from urllib.parse import quote

app = Flask(__name__)


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
        integrations = response.json().get('items', [])
        # Filter integrations to only include those that start with the pattern
        return [integration for integration in integrations if integration['name'].startswith(pattern)]
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

    results = []

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
                results.append(
                    f"Integration {integration_id} successfully updated to {status} with payloadTracingEnabledFlag: {payload.get('payloadTracingEnabledFlag', False)}")
            else:
                results.append(f"Failed to update integration {integration_id}: {response.status_code} {response.text}")
        else:
            results.append(f"Integration {integration_id} is locked or could not be retrieved.")

    return results


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/update_status', methods=['POST'])
def update_status():
    oic_instance = request.form['oic_instance']
    username = request.form['username']
    password = request.form['password']
    pattern = request.form['pattern']
    status = request.form['status']
    single_integration_id = request.form['single_integration_id']

    if single_integration_id:
        integration_ids = [single_integration_id]
    else:
        integration_list = get_integration_list(oic_instance, username, password, pattern)
        integration_ids = [f"{integration['code']}|{integration['version']}" for integration in integration_list]

    results = update_integration_status(oic_instance, username, password, integration_ids, status)
    return render_template('result.html', results=results)


if __name__ == '__main__':
    app.run(debug=True)
