import requests
import time
import json

def main():    
    CHECK_PERIOD = 1 * 60

    lastChecked = 0
    while True:
        while time.time() - lastChecked < CHECK_PERIOD:
            time.sleep(0.5)
        
        try:
            response = requests.get('https://api.wallex.ir/v1/currencies/stats')

            with open('data.json', 'w', encoding='utf-8') as f:
                json.dump(response.json(), f, indent=4, ensure_ascii=False)
            
            time.sleep(5)

            response = requests.get('https://api.wallex.ir/v1/markets')

            with open('data2.json', 'w', encoding='utf-8') as f:
                json.dump(response.json(), f, indent=4, ensure_ascii=False)
            
            lastChecked = time.time()

        except:
            pass