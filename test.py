import requests

# Assuming your Flask app is running on localhost:5000
BASE_URL = 'http://localhost:5000'

def test_get_budget_alert():
    username = '66a87750199223aa813ce3ad'
    url = f'{BASE_URL}/budget/alert/{username}'
    
    response = requests.get(url)
    
    print(f'Status Code: {response.status_code}')
    print(f'Response: {response.json()}')
    
    if response.status_code == 200:
        if 'alert' in response.json():
            print(f"Test passed: Budget alert received - {response.json()['alert']}")
        elif 'message' in response.json():
            print(f"Test passed: No budget alert - {response.json()['message']}")
        else:
            print("Test failed: Unexpected response format")
    else:
        print('Test failed: Could not get budget alert')




if __name__ == '__main__':
    print("Testing set_budget with valid data:")
    test_get_budget_alert()
    
   