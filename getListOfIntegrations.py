# script Iterates over list of integration IDs - returns all data about each integration that has 'INT_'
import requests

# Replace these variables with your Oracle Integration Cloud details
OIC_INSTANCE = 'oic_instance'
OIC_USERNAME = 'user.name'
OIC_PASSWORD = 'pwd'

# Set up session for persistent connection with authentication
session = requests.Session()
session.auth = (OIC_USERNAME, OIC_PASSWORD)
# parameters = '{name: /INT_/, status: "ACTIVATED"}'

# API endpoint to retrieve integration IDs with a specific name pattern
integrations_url = f'https://{OIC_INSTANCE}/ic/api/integration/v1/integrations?q={{name:/INT_/}}'

try:

    # Make the request to retrieve integration data
    response = session.get(integrations_url)
    response.raise_for_status()

    # Parse the response content as JSON
    integration_data = response.json()

    # Extract integration names starting with 'INT_'
    integration_names = [integration['name']
                         for integration in integration_data.get('items', [])
                         if integration['name'].startswith('INT_')]

    # Print or use the filtered integration names as needed
    print("Integration Names starting with 'INT_':", integration_names)


except requests.exceptions.RequestException as e:
    print(f"Error: {e}")

finally:
    # Close the session
    session.close()
