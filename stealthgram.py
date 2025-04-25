from curl_cffi import requests
from time import sleep
import json

HEADERS = { # Headers for session
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Geck   o) Chrome/131.0.0.0 Safari/537.36"
}

stealthgram_tokens = None # Global variable for stealthgram tokens

def send_request(url, method='POST', payload=None, headers=None, retries=3, timeout=60):
    '''
    Sends a request to the url and returns the response

    Parameters:
        url (str): The url to send the request
        method (str): The method for the request
        payload (str): The payload for the request
        headers (dict): The headers for the request
        retries (int): The number of retries for the request
        timeout (int): The timeout for the request
    
    Returns:
        response (requests.Response): The response of the request
    '''

    try:
        response = requests.request(method=method, url=url, data=payload, headers=headers if headers is not None else HEADERS, timeout=timeout, impersonate='chrome124') # Send the request
        
        if response.status_code == 200:
            return response # Return the response
        
        elif (response.status_code) == 429 and (retries > 0): # Too many requests
            sleep(30) # Sleep for 30 seconds

            return send_request(url=url, method=method, payload=payload, headers=headers, retries=retries-1) # Try again
        
        else:
            return None # Couldn't get the data
    
    except:
        return None # Couldn't get the data

def update_stealthgram_tokens(headers):
    '''
    Updates the stealthgram tokens

    Parameters:
        headers (Headers): The headers of the request
    
    Returns:
        result (bool): If the tokens are updated successfully or not
    '''

    try:
        set_cookies = headers.get('set-cookie').split(' ') # Get the set-cookie's from the headers

        found = 0 # Number of tokens found
        
        global stealthgram_tokens
        for cookie in set_cookies:
            if 'access-token' in cookie:
                stealthgram_tokens['access-token'] = cookie[cookie.index('=') + 1:cookie.index(';')]
                found += 1
            
            elif 'refresh-token' in cookie:
                stealthgram_tokens['refresh-token'] = cookie[cookie.index('=') + 1:cookie.index(';')]
                found += 1
            
            if found == 2:
                break # Found both tokens
    
        return True # Tokens updated successfully
    
    except:
        return False # Couldn't update the tokens

def get_stealthgram_tokens():
    '''
    Gets the stealthgram tokens

    Returns:
        result (bool): If the tokens are updated successfully or not
    '''

    try:
        url = 'https://stealthgram.com/'

        response = send_request(url=url, method='GET', headers=HEADERS) # Get the data

        if response is None:
            return False # Couldn't get the tokens
        
        global stealthgram_tokens
        stealthgram_tokens = {} # Empty the tokens

        if update_stealthgram_tokens(headers=response.headers):
            return True # Tokens updated successfully

        stealthgram_tokens = None # Tokens are not available

        return False # Couldn't get the tokens
    
    except:
        stealthgram_tokens = None # Tokens are not available
        return False # Couldn't get the tokens

def call_stealthgram_api(info, task):
    '''
    Calls the stealthgram API to get the data

    Parameters:
        info (list): The information needed for the task
        task (str): The task to perform
    
    Returns:
        response (requests.Response): The response of the request
    '''
    
    try:
        # Base API link
        link = "https://stealthgram.com/api/apiData"

        # Set the payload for the request
        if task == 'highlight': # If the data is for highlight
            payload = json.dumps({
                "body": {
                    "id": str(info[0]),
                },
                "url": "user/get_highlights"
            })
        
        elif task == 'PK': # If the data is for finding the pk
            payload = json.dumps({
                "body": {
                    "query": info[0],
                },
                "url": "user/search"
            })
        
        elif task == 'story': # If the data is for story
            payload = json.dumps({
                "body": {
                    "ids": [
                        info[0]
                    ],
                },
                "url": "user/get_stories"
            })
                
        elif task == 'highlight_story': # If the data is for highlight story
            payload = json.dumps({
                "body": {
                    "ids": [
                        str(info[0])
                    ],
                },
                "url": "highlight/get_stories"
            })
        
        # Check if stealthgram tokens are available
        global stealthgram_tokens
        if stealthgram_tokens is None:
            if not get_stealthgram_tokens():
                return None # Couldn't update the tokens
        
        # Set the headers for the request
        headers = {
            'Cookie': f"access-token={stealthgram_tokens['access-token']}; refresh-token={stealthgram_tokens['refresh-token']};",
        }
        headers.update(HEADERS) # Add the default headers to the request

        response = send_request(url=link, payload=payload, headers=headers) # Get the data

        update_stealthgram_tokens(headers=response.headers) # Update the stealthgram tokens

        return response # Return the response
    
    except:
        return None # There was an error

def get_pk_username(pk):
    '''
    Gets the username of the given pk

    Parameters:
        pk (int): The pk of the profile
    
    Returns:
        username (str): The username of the profile
    '''

    try:
        url = f'https://i.instagram.com/api/v1/users/{pk}/info/' # The url to get the profile's data

        headers = {
            'User-Agent': 'Instagram 85.0.0.21.100 Android (23/6.0.1; 538dpi; 1440x2560; LGE; LG-E425f; vee3e; en_US)',
        }

        response = send_request(url=url, method='GET', headers=headers).json() # Get the profile's data

        if 'user' in response.keys(): # If the data is found
            return response['user']['username']
        
        return None # Couldn't get the username
    
    except:
        return None # Couldn't get the data

def get_username_pk(username):
    '''
    Gets the pk of the given username

    Parameters:
        username (str): The username of the profile
    
    Returns:
        pk (int): The pk of the profile
    '''

    try:
        response = call_stealthgram_api(info=[username], task='PK') # Get the pk of the profile

        if response is None:
            return None # Couldn't get the data
        
        data = response.json() # Get the data
        data = data['response']['body']['users']

        if len(data) > 0: # If the data is found
            for user in data:
                if user['username'] == username:
                    return user['pk']
        
        return None # Couldn't get the pk
    
    except:
        return None # Couldn't get the data

def get_stories_data(pk, highlight_id):
    '''
    Gets the stories (or highlights) data of the profile

    Parameters:
        pk (int): The profile's pk
        highlight_id (int): The highlight's id
    
    Returns:
        data (list): The stories data
    '''

    try:
        if pk == highlight_id: # If the data is for the profile's stories
            response = call_stealthgram_api(info=[pk], task='story') # Get the stories data
        
        else: # If the data is for the highlight's stories
            response = call_stealthgram_api(info=[highlight_id], task='highlight_story') # Get the stories data

        if response is None:
            return None # Couldn't get the data

        data = json.loads(response.text) # Parse the data to json

        # Set the label for getting the stories from the response
        label = ('highlight:' if pk != highlight_id else '') + str(highlight_id)

        # If there is currently no story or highlight
        if label not in data['response']['body']['reels'].keys():
            return [] # Return an empty list
        
        else: # If there is a story or highlight
            data = data['response']['body']['reels'][label]['items']

        return data # Return the stories data
    
    except:
        return None # Couldn't get the stories data

def get_story_link(username, story_pk):
    '''
    Gets the story's link

    Parameters:
        username (str): The username of the profile
        story_pk (int): The pk of the story
    
    Returns:
        link (str): The link of the story
    '''

    try:
        pk = get_username_pk(username=username) # Get the pk of the profile

        data = get_stories_data(pk=pk, highlight_id=pk) # Get the stories data

        if data is None:
            return None # Couldn't get the data
        
        for story in data: # Find the story with the given pk
            this_story_pk = int(story['id'][:story['id'].find('_')]) # The story's pk

            if this_story_pk == story_pk: # If the story is found
                if 'video_versions' in story.keys(): # If the story is video
                    return 'video', story['video_versions'][0]['url'].replace("se=7&", "") # Get the video link (better quality)

                return 'photo', story['image_versions2']['candidates'][0]['url'].replace("se=7&", "") # Get the picture link (better quality)
        
        return None # Couldn't get the link
    
    except:
        return None # Couldn't get the data

def get_highlights_data(pk):
    '''
    Gets the highlights data of the profile

    Parameters:
        pk (int): The profile's pk
    
    Returns:
        data (list): The highlights data
    '''

    try:
        response = call_stealthgram_api(info=[pk], task='highlight') # Get the highlights data

        if response is None: # Couldn't get the highlights data
            return None
        
        data = json.loads(response.text)
        data = data['response']['body']['data']['user']['edge_highlight_reels']['edges']

        return data # Return the highlights data
    
    except:
        return None # Couldn't get the highlights data

def get_highlight_story_link(pk, story_pk):
    '''
    Gets the link of the highlight's story

    Parameters:
        pk (int): The pk of the profile
        story_pk (int): The pk of the story
    
    Returns:
        link (str): The link of the story
    '''

    try:
        highlights_data = get_highlights_data(pk=pk) # Get the highlights data

        if highlights_data is None:
            return None # Couldn't get the data
        
        for highlight in highlights_data: # Find the story with the given pk
            highlight_id = int(highlight['node']['id'])

            data = get_stories_data(pk=pk, highlight_id=highlight_id) # Get the stories data

            if data is None:
                continue # Couldn't get the data

            for story in data: # Find the story with the given pk
                this_story_pk = int(story['id'][:story['id'].find('_')])

                if this_story_pk == story_pk: # If the story is found
                    if 'video_versions' in story.keys():
                        return 'video', story['video_versions'][0]['url'].replace("se=7&", "")
                    
                    return 'photo', story['image_versions2']['candidates'][0]['url'].replace("se=7&", "")
            
        return None # Couldn't get the link
    
    except:
        return None # Couldn't get the data