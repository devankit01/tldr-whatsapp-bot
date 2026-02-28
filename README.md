# TLDR → WhatsApp Pipeline

Fetches your TLDR newsletter emails, summarizes them with Claude, and sends the summary to your WhatsApp every morning. Completely free except for Claude API (~$0.01/day).

## Stack
- **Gmail API** — fetch emails (free)
- **Claude API** — summarize (~ $0.01/day)
- **CallMeBot** — send WhatsApp (free)
- **APScheduler** — run daily at set time (free)

---

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Gmail API credentials
1. Go to https://console.cloud.google.com
2. Create a new project
3. Enable **Gmail API**
4. Go to **Credentials** → Create **OAuth 2.0 Client ID** → Desktop App
5. Download the JSON and save as `credentials.json` in the project root
6. First run will open a browser for consent — after that it's automatic

### 3. CallMeBot WhatsApp API (free)
1. Save `+34 644 59 75 10` as a contact named **CallMeBot**
2. Send this exact message to that number on WhatsApp:
   ```
   I allow callmebot to send me messages
   ```
3. You'll receive your API key via WhatsApp within a few seconds

### 4. Configure .env
```bash
cp .env.example .env
```
Fill in:
```
ANTHROPIC_API_KEY=your_key
WHATSAPP_PHONE=+1234567890
WHATSAPP_APIKEY=your_callmebot_key
SCHEDULE_HOUR=8
SCHEDULE_MINUTE=0
```

### 5. Run
```bash
python main.py
```
Runs immediately on startup, then every day at your scheduled time.

---

## Project Structure
```
tldr_whatsapp/
├── app/
│   ├── gmail_client.py      # fetch TLDR emails from Gmail
│   ├── summarizer.py        # summarize with Claude
│   ├── whatsapp_sender.py   # send via CallMeBot
│   ├── pipeline.py          # orchestrates the flow
│   └── logger.py            # logging setup
├── logs/
│   └── app.log              # auto-created on first run
├── credentials.json         # from Google Cloud Console (you add this)
├── token.json               # auto-created after first OAuth consent
├── main.py                  # entry point + scheduler
├── requirements.txt
└── .env                     # your secrets (never commit this)
```

---

## Cost Breakdown
| Service | Cost |
|---|---|
| Gmail API | Free |
| CallMeBot WhatsApp | Free |
| Claude API (claude-sonnet) | ~$0.01 per summary |
| Hosting (your machine/VPS) | Free / ~$4/month |
