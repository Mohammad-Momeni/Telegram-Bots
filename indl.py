import requests
from stealthgram import get_story_link, get_highlight_story_link
from downloader import try_downloading
from imginn import get_single_post_data
import json
import re
from datetime import datetime
from contextlib import ExitStack
import os

path = os.path.dirname(os.path.abspath(__file__))

with open('tokens.json', 'r', encoding='utf-8') as f:
    tokens = json.load(f)

BOT_TOKEN = tokens['IN_DL']  # Instagram downloader bot token

# Telegram API URL for sending messages
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_message(chat_id, caption, files_info):
    '''
    Function to send message to a chat

    Parameters:
        chat_id (int): Chat ID to send the message
        caption (str): Caption of the message
        files_info (list): Files to send in the message

    Returns:
        Result (dict): JSON response from the Telegram API
    '''

    url = f"{TELEGRAM_API_URL}/sendMediaGroup"

    media = []

    for i, (file_key, _) in enumerate(files_info):
        media.append({
            "type": 'photo' if 'photo' in file_key else 'video',
            "media": f"attach://{file_key}",
        })

        if (caption is not None) and (i == 0):
            media[i]["caption"] = caption
    
    # Prepare the data payload.
    data = {
        "chat_id": chat_id,
        "media": json.dumps(media)  # media must be a JSON-encoded string.
    }

    # Use ExitStack to open all files at once.
    with ExitStack() as stack:
        files = {}

        for file_key, file_path in files_info:
            files[file_key] = stack.enter_context(open(file_path, "rb"))
        
        # Send the request with the opened files.
        response = requests.post(url, data=data, files=files)

    return response.json()

def instagram_link(text):
    '''
    Function to extract Instagram link from text

    Parameters:
        text (str): Text to extract link from

    Returns:
        links (list): List of links extracted from the text
    '''

    try:
        pattern = r'https?://(?:www\.)?instagram\.com/[^\s]+'
        links = re.findall(pattern, text)
        
        if len(links) > 0:
            return links
        
        return None # No link found
    
    except:
        return None # Error extracting link

def handle_posts(chat_id, shortcode):
    '''
    Function to handle Instagram posts

    Parameters:
        chat_id (int): Chat ID to send the message
        shortcode (str): Instagram post shortcode to handle
    '''

    try:
        data = get_single_post_data(post_code=shortcode)
        
        if data is None:
            return # Couldn't get the post data
        
        caption, timestamp, links = data

        date = datetime.fromtimestamp(timestamp)

        caption = caption + '\n\n' + f"Posted on: {date.strftime('%Y-%m-%d %H:%M:%S')}"

        files_info = []

        for i, (link, item_type) in enumerate(links):
            result = try_downloading(link=link, address=os.path.join(path, 'downloads', f"{shortcode}_{i}"))

            if result == False:
                return # Couldn't download the post
            
            files_info.append((item_type + str(i), os.path.join(path, 'downloads', f"{shortcode}_{i}" + result)))
        
        send_message(chat_id=chat_id, caption=caption, files_info=files_info)

        for _, file_path in files_info:
            os.remove(file_path)
        
    except Exception as e:
        print("Error handling Instagram post:", e)

def handle_stories(chat_id, username, story_pk):
    '''
    Function to handle Instagram stories

    Parameters:
        chat_id (int): Chat ID to send the message
        username (str): Instagram username to handle
        story_pk (int): Instagram story pk to handle
    '''

    try:
        result = get_story_link(username=username, story_pk=story_pk)

        if result is None:
            return # Couldn't get the story link
        
        story_type, story_link = result
        
        result = try_downloading(story_link, os.path.join(path, 'downloads', f"{username}_{story_pk}"))

        if result == False:
            return # Couldn't download the story
        
        files_info = [
            (story_type + '1', os.path.join(path, 'downloads', f"{username}_{story_pk}" + result))
        ]

        send_message(chat_id=chat_id, caption=None, files_info=files_info)

        os.remove(os.path.join(path, 'downloads', f"{username}_{story_pk}" + result))
    
    except Exception as e:
        print("Error handling Instagram story:", e)

def handle_highlight_stories(chat_id, pk, story_pk):
    '''
    Function to handle Instagram highlight stories

    Parameters:
        chat_id (int): Chat ID to send the message
        pk (int): Instagram user pk to handle
        story_pk (int): Instagram story pk to handle
    '''

    try:
        result = get_highlight_story_link(pk=pk, story_pk=story_pk)

        if result is None:
            return # Couldn't get the story link
        
        story_type, story_link = result

        result = try_downloading(link=story_link, address=os.path.join(path, 'downloads', f"{pk}_{story_pk}"))

        if result == False:
            return # Couldn't download the story
        
        files_info = [
            (story_type + '1', os.path.join(path, 'downloads', f"{pk}_{story_pk}" + result))
        ]

        send_message(chat_id=chat_id, caption=None, files_info=files_info)

        os.remove(os.path.join(path, 'downloads', f"{pk}_{story_pk}" + result))
    
    except Exception as e:
        print("Error handling Instagram highlight story:", e)

def handle_instagram_link(chat_id, link):
    '''
    Function to handle Instagram link

    Parameters:
        chat_id (int): Chat ID to send the message
        link (str): Instagram link to handle
    '''

    try:
        if '/p/' in link:
            shortcode = link.split('/p/')[1].split('/')[0]
            
            handle_posts(chat_id=chat_id, shortcode=shortcode)
        
        elif '/reel/' in link:
            shortcode = link.split('/reel/')[1].split('/')[0]
            
            handle_posts(chat_id=chat_id, shortcode=shortcode)
        
        elif '/stories/' in link:
            detail = link.split('/stories/')[1]

            username = detail.split('/')[0]

            story_pk = detail.split('/')[1]
            story_pk = int(story_pk.split('?')[0])
            
            handle_stories(chat_id=chat_id, username=username, story_pk=story_pk)
        
        elif 'story_media_id' in link:
            detail = link.split('story_media_id=')[1].split('&')[0]
            detail = detail.split('_')

            pk = int(detail[1])
            story_pk = int(detail[0])
            
            handle_highlight_stories(chat_id=chat_id, pk=pk, story_pk=story_pk)
    
    except Exception as e:
        print("Error handling Instagram link:", e)