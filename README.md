# 📬 Telegram Bot Structure

This project is a lightweight Telegram bot structure built with **FastAPI** that receives updates using **webhooks**, without using external libraries.

---

## 🚀 Features

- Uses native HTTP methods with FastAPI
- Webhook-based: no long polling
- Logs users who interact with the bot (private users, groups, or channels)
- No external dependencies beyond FastAPI and standard libraries
- Compatible with **ngrok** for local development

---

## 🛠️ Requirements

- Python 3.7+
- [FastAPI](https://fastapi.tiangolo.com/)
- [ngrok](https://ngrok.com/) (for local webhook tunneling)
- A Telegram bot token from [@BotFather](https://t.me/BotFather)

---

## 📂 File Structure

```
.
├── main.py          # Main FastAPI bot server
├── wallex_bot.py    # Wallex bot
├── wallex.py        # Gets Wallex data
├── indl.py          # Instagram downloader bot
├── imginn.py        # Gets Instagram posts data
├── stealthgram.py   # Gets Instagram stories data
├── downloader.py    # Downloads data
├── users.json       # Stores chat/user info
├── downloads/       # Folder to temporarily store downloaded data
└── README.md
```

---

## ⚙️ How It Works

Telegram sends updates to your bots via **webhooks** — it posts JSON data to your server's `/webhook` endpoint whenever a user interacts with the bot.

We then:
- Extract the data from the update
- Process the data
- Respond to the message

---

## 📌 How to Run

1. **Install FastAPI and Uvicorn**
   ```bash
   pip install fastapi uvicorn
   ```

2. **Start the bot server**
   ```bash
   uvicorn bot:app --host 0.0.0.0 --port 8000
   ```

3. **Expose your local server with ngrok**
   ```bash
   ngrok http 8000
   ```

   You will get a public HTTPS URL like:
   ```
   https://<your-subdomain>.ngrok.io
   ```

4. **Set the webhook**
   Replace `<BOT_TOKEN>` with your actual bot token and run:

   ```bash
   curl -X POST "https://api.telegram.org/bot<BOT_TOKEN>/setWebhook" \
        -d "url=https://<your-subdomain>.ngrok.io/webhook"
   ```

   You should get a response like:
   ```json
   {"ok":true,"result":true,"description":"Webhook was set"}
   ```

---

## 🧠 Example Log (users.json)

```json
[
  {
    "chat_id": 123456789,
    "chat_type": "private",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe"
  },
  {
    "chat_id": -1009876543210,
    "chat_type": "supergroup",
    "username": "someuser",
    "title": "Awesome Group"
  }
]
```

---

## 📎 Notes

- Bots only track users to keep track of bot usage and don't store any private information.

---

## 📜 License

MIT License
