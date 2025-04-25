from curl_cffi import requests
import base64

def get_auth_token(username):
    '''
    Function to get the authentication token for the given username

    Parameters:
        username (str): Username to get the authentication token for

    Returns:
        auth (str): Authentication token for the given username
    '''

    try:
        key = "LTE6Om11cmllbGdhbGxlOjpySlAydEJSS2Y2a3RiUnFQVUJ0UkU5a2xnQldiN2Q="

        # Equivalent to Base64 encoding of "-1::" + username + "::" + key
        auth = base64.b64encode(f"-1::{username}::{key}".encode()).decode()

        # Replace characters as per the JavaScript regex replacements
        auth = auth.replace("+", ".").replace("/", "_").replace("=", "-")

        return auth # Return the authentication token

    except:
        return None # Error getting the authentication token

def get_data(username):
    '''
    Function to get the data for the given username

    Parameters:
        username (str): Username to get the data for

    Returns:
        data (dict): Data for the given username
    '''

    try:
        auth = get_auth_token(username) # Get the authentication token

        if auth is not None:
            url = "https://anonstories.com/api/v1/story" # Define the URL

            payload = {
                "auth": auth
            } # Define the payload

            response = requests.post(url, data=payload) # Send the POST request

            if response.status_code == 200:
                data = response.json() # Get the JSON data

                if 'stories' in data.keys():
                    return data['stories'] # Return the stories data
                
        return None # No stories data found

    except:
        return None # Error getting the data

def get_story(username, story_pk):
    '''
    Function to get the story with the given story_pk for the given username

    Parameters:
        username (str): Username to get the story for
        story_pk (int): Story PK to get the story for

    Returns:
        story (dict): Story for the given username and story_pk
    '''

    try:
        stories_data = get_data(username) # Get the stories data

        if stories_data is not None:
            for story in stories_data:
                if story['pk'] == story_pk:
                    return story

    except:
        return None # Error getting the story