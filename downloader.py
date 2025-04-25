from mimetypes import guess_extension
import requests

HEADERS = { # Headers for the requests
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}

def download_link(link, address):
    '''
    Downloads the link and saves it to the address

    Parameters:
        link (str): The link to download
        address (str): The address to save the file
    
    Returns:
        result (bool): If the link is downloaded successfully or not
    '''

    try:
        media = requests.get(link, headers=HEADERS, timeout=60, allow_redirects=True) # Get the media from the link
        
        extension = guess_extension(media.headers['content-type'].partition(';')[0].strip()) # Find the extension from the headers
        if extension is None: # If couldn't find from headers then find from the link
            extension = link[:link.index('?')]
            extension = extension[extension.rindex('.'):]
        
        if extension in [None, '', '.', '.txt', '.html']: # If couldn't find the extension or it's a text or html file (Probably an error)
            return False # Couldn't download the link
        
        open(address + extension, 'wb').write(media.content) # saving the file
        return extension
    
    except:
        return False # Couldn't download the link

def try_downloading(link, address, retries=3):
    '''
    Tries to download the link for retries times

    Parameters:
        link (str): The link to download
        address (str): The address to save the file
        retries (int): The number of retries for the download
    
    Returns:
        result (bool): If the link is downloaded successfully or not
    '''

    isDownloaded = download_link(link=link, address=address) # Try downloading the link

    if isDownloaded == False: # If couldn't download the link, Try retries times
        for _ in range(retries):
            isDownloaded = download_link(link=link, address=address) # Try downloading the link

            if isDownloaded != False: # If downloaded the link
                return isDownloaded # Return the extension
        
        return False # Couldn't download the link
        
    return isDownloaded