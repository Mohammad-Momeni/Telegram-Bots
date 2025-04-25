import requests
import threading
import wallex
import json

with open('tokens.json', 'r', encoding='utf-8') as f:
    tokens = json.load(f)

BOT_TOKEN = tokens['WALLEX']  # Wallex bot token

# Telegram API URL for sending messages
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

threading.Thread(target=wallex.main).start()

def send_message(chat_id, text):
    '''
    Function to send message to a chat

    Parameters:
    chat_id (int): Chat ID to send the message
    text (str): Text message to send

    Returns:
    Result (dict): JSON response from the Telegram API
    '''

    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }

    response = requests.post(url, data=payload)

    return response.json()

def send_coin_info(chat_id, data2, cryptoKey):
    """
    Function to send coin info to a chat

    Parameters:
    chat_id (int): Chat ID to send the message
    data2 (dict): Data dictionary containing coins info
    cryptoKey (str): Cryptocurrency symbol to get info
    """
    
    if cryptoKey == 'USDT':
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for key in data['result']:
            if key['key'] == cryptoKey.strip():
                usd_price = key['price']
                break
    
    else:
        usd_price = float(data2['result']['symbols'][cryptoKey + "USDT"]['stats']['lastPrice'])

    if usd_price > 1:
        usd_price = f"{usd_price:.2f}"
    
    toman_price = float(data2['result']['symbols'][cryptoKey + 'TMN']['stats']['lastPrice'])

    if toman_price > 1:
        toman_price = f"{toman_price:.2f}"
    
    if cryptoKey == 'USDT':
        percent_change_24h = data2['result']['symbols'][cryptoKey + "TMN"]['stats']['24h_ch']
    
    else:
        percent_change_24h = data2['result']['symbols'][cryptoKey + "USDT"]['stats']['24h_ch']

    if percent_change_24h > 0:
        sign = '🟢'
        
    else:
        sign = '🔴'
    
    if cryptoKey == 'USDT':
        en_name = data2['result']['symbols'][cryptoKey + "TMN"]['enName']
    
    else:
        en_name = data2['result']['symbols'][cryptoKey + "USDT"]['enName']
    
    en_name = en_name.split(' ')[0]
    
    send_message(chat_id, f"{en_name} ({cryptoKey}):\nUSD: ${usd_price}\nToman: {toman_price}\n\n{sign} Percent change (24H): %{percent_change_24h}")