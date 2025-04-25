from fastapi import FastAPI, Request
import uvicorn
import json
import os
import wallex_bot
import indl
app = FastAPI()

def save_user_info(message, file_path="users.json"):
    chat = message.get("chat", {})
    sender = message.get("from", {})

    chat_id = chat.get("id")
    chat_type = chat.get("type")

    entry = {
        "chat_id": chat_id,
        "chat_type": chat_type,
        "username": sender.get("username", None)
    }

    if chat_type == "private":
        entry["first_name"] = sender.get("first_name", "")
        entry["last_name"] = sender.get("last_name", "")
    
    else:
        entry["title"] = chat.get("title", "")

    # Load existing data
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    # Append new entry
    data.append(entry)

    # Save back to file
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

@app.post("/wallex")
async def handle_update(request: Request):
    """
    Function to handle incoming webhook updates

    Parameters:
    request (Request): Request object containing the update

    Returns:
    Result (dict): JSON response to the update
    """

    try:
        update = await request.json()

        # Extract chat_id and message from the update
        chat_id = update['message']['chat']['id']
        text = update['message'].get('text', '')

        # Log the update
        print("Update received:", update)

        # Extract chat ID and message text
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")

        # Save user info to JSON file
        try:
            save_user_info(update["message"])
        
        except Exception as e:
            print("Error saving user info:", e)

        if text == "/start":
            wallex_bot.send_message(chat_id, "Welcome to Crypto Price Bot!")
            wallex_bot.send_message(chat_id, "Type the symbol of the cryptocurrency to get the price.\n Enter /help to get the list of available cryptocurrencies")
            return {"status": "ok"}
        
        with open('data2.json', 'r', encoding='utf-8') as f:
            data2 = json.load(f)
        
        if text == "/help":
            tokens = [token for token in data2['result']['symbols'].keys() if 'USDT' in token]

            reply = "Available cryptocurrencies:\n"

            for token in tokens:
                reply += f"En: {token.replace('USDT', '').replace('TMN', '') if token != 'USDTTMN' else token.replace('TMN', '')}       Fa: " + data2['result']['symbols'][token]['faBaseAsset'] + "\n"
            
            wallex_bot.send_message(chat_id, reply.strip())
            return {"status": "ok"}

        cryptoKey = text.upper().strip()
        
        if cryptoKey + "USDT" in data2['result']['symbols'] or cryptoKey == 'USDT':
            wallex_bot.send_coin_info(chat_id, data2, cryptoKey)
            return {"status": "ok"}
        
        else:
            for key in data2['result']['symbols'].keys():
                asset = data2['result']['symbols'][key]['faBaseAsset']

                if cryptoKey == asset.split(' ')[0].strip() or cryptoKey == asset.strip():
                    if 'USDTTMN' == key:
                        wallex_bot.send_coin_info(chat_id, data2, key.replace('TMN', ''))
                    
                    else:
                        wallex_bot.send_coin_info(chat_id, data2, key.replace('USDT', '').replace('TMN', ''))
                    
                    return {"status": "ok"}

        return {"status": "ok"}
    
    except Exception as e:
        print("Error handling update:", e)
        return {"status": "error"}

@app.post("/indl")
async def handle_update(request: Request):
    '''
    Function to handle incoming webhook updates

    Parameters:
        request (Request): Request object containing the update

    Returns:
        Result (dict): JSON response to the update
    '''

    try:
        update = await request.json()

        # Extract chat_id and message from the update
        chat_id = update['message']['chat']['id']
        text = update['message'].get('text', '')

        # Log the update
        print("Update received:", update)

        # Save user info to JSON file
        try:
            save_user_info(update["message"])
        
        except Exception as e:
            print("Error saving user info:", e)

        # Check if there's an Instagram link in the message
        links = indl.instagram_link(text=text)

        if links is not None:
            for link in links:
                indl.handle_instagram_link(chat_id=chat_id, link=link)

        return {"status": "ok"}
    
    except Exception as e:
        print("Error handling update:", e)
        return {"status": "error"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)