from stealthgram import send_request
from bs4 import BeautifulSoup
from urllib.parse import unquote

def call_post_page_api(post_code):
    '''
    Calls the API for the post page

    Parameters:
        post_code (str): The post's code
    
    Returns:
        soap (BeautifulSoup): The post data
    '''

    try:
        link = f"https://imginn.com/p/{post_code}" # The link for the post page

        response = send_request(url=link, method='GET') # Get the data

        if response is None:
            return None # Couldn't get the data
        
        soap = BeautifulSoup(response.text, 'html.parser') # Parse the response using BeautifulSoup to get the data

        return soap # Return the data
    
    except:
        return None # Couldn't get the data

def get_single_post_data(post_code):
    '''
    Gets the data of a single post

    Parameters:
        post_code (str): The post's code
    
    Returns:
        data (tuple): The post data
    '''

    try:
        soap = call_post_page_api(post_code=post_code) # Get the data

        if soap is None:
            return None # Couldn't get the post data
        
        data = soap.find(attrs={'class': 'page-post'}) # Find the post data

        try:
            caption = data.find(attrs={'class': 'desc'}).text.strip() # Get the caption of the post
        
        except:
            caption = '' # Post doesn't have a caption

        timestamp = int(data.get_attribute_list('data-created')[0]) # Get the timestamp of the post

        links = [] # List of media links

        single_media = False # Flag for if the post has single media

        try:
            swiper = data.find(attrs={'class': 'swiper-wrapper'}) # Get the swiper of the post

            if swiper is not None: # If the post has multiple media
                try:
                    slide = swiper.find_all(attrs={'class': 'swiper-slide'}) # Get the slides of the post

                    for item in slide:
                        item_type = 'photo' # The type of the media

                        if item.find('video') is not None: # If the media is video
                            item_type = 'video' # Set the type to video
                        
                        link = item.get_attribute_list('data-src')[0] # Get the media link

                        if 'null.jpg' in link: # If the media link is null
                            link = item.find(item_type).attrs['poster'] # Get the poster link instead
                            item_type = 'photo' # Set the type to image
                        
                        links.append((link, item_type)) # Add the media link to the list
                
                except:
                    return None # Couldn't get the post data
            
            else: # If the post has single media
                single_media = True # The post has single media
        
        except: # If the post has single media
            single_media = True # The post has single media

        if single_media: # If the post has single media
            download = data.find(attrs={'class': 'downloads'}) # Get the download section of the post

            if download is not None: # If the post has download section
                media = data.find(attrs={'class': 'media-wrap'}) # Get the media of the post

                item_type = 'photo' # The type of the media

                if len(media.get_attribute_list('class')) == 2: # If the media is video
                    item_type = 'video' # Set the type to video

                link = download.find('a').attrs['href'] # Get the media link

                if 'u=' in link: # If the media link is from google translation
                    link = link[link.index('u=') + 2:] # Get rid of google translation part of the link

                    link = unquote(link) # Decode the link

                if 'null.jpg' in link: # If the media link is null
                    link = media.find(item_type).attrs['poster'] # Get the poster link instead
                    item_type = 'photo' # Set the type to image

                if '&dl' in link: # If the media link is direct download link
                    link = link[:link.index('&dl')] # Get the media link
                
                links.append((link, item_type)) # Add the media link to the list
        
        return (caption, timestamp, links) # Return the post data
    
    except:
        return None # Couldn't get the post data