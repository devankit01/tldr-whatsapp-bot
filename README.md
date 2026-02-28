```markdown
# TLDR → WhatsApp Pipeline

Fetches your TLDR newsletter emails from the last 24 hours, summarizes them in Inshorts style using OpenAI, and sends the summary to your WhatsApp via Twilio every morning.

## Stack
- **Gmail IMAP** — fetch emails (free, no OAuth needed)
- **OpenAI GPT-4o mini** — summarize (~$0.001/day)
- **Twilio WhatsApp** — send message (~$0.005/message)
- **APScheduler** — run daily at set time (free)
- **Railway** — cloud hosting (free tier)

---

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Gmail App Password (no OAuth needed)
1. Go to https://myaccount.google.com/security
2. Enable **2-Step Verification**
3. Go to https://myaccount.google.com/apppasswords
4. Select **Mail** → **Mac** → Click **Generate**
5. Copy the 16-character password

### 3. OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Click **Create new secret key**
3. Copy the key

### 4. Twilio WhatsApp
1. Sign up at https://www.twilio.com (free $15 trial credit)
2. Go to **Messaging** → **Try it out** → **Send a WhatsApp message**
3. Send the join code to `+1 415 523 8886` on WhatsApp
4. Copy **Account SID** and **Auth Token** from dashboard

### 5. Configure .env
```bash
cp .env.example .env
```
Fill in:
```
OPENAI_API_KEY=your_openai_api_key
GMAIL_EMAIL=your@gmail.com
GMAIL_APP_PASSWORD=abcdefghijklmnop
TLDR_SENDER=dan@tldrnewsletter.com
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
TWILIO_WHATSAPP_TO=whatsapp:+1234567890
SCHEDULE_HOUR=8
SCHEDULE_MINUTE=0
```

### 6. Run locally
```bash
python main.py
```
Runs immediately on startup, then every day at your scheduled time.

---

## Deploy to Railway (recommended)

```bash
# 1. add secrets to .gitignore
echo ".env" >> .gitignore
git init
git add .
git commit -m "initial commit"
git push origin main
```

1. Go to https://railway.app → sign in with GitHub
2. Click **New Project** → **Deploy from GitHub repo**
3. Select your repo
4. Go to **Variables** tab → add all your `.env` values
5. Click **Deploy** ✅

Railway auto-redeploys on every `git push`.

---

## Project Structure
```
tldr_whatsapp/
├── app/
│   ├── gmail_client.py      # fetch TLDR emails via IMAP (last 24hrs)
│   ├── summarizer.py        # summarize with OpenAI GPT-4o mini
│   ├── whatsapp_sender.py   # send via Twilio WhatsApp
│   ├── pipeline.py          # orchestrates the full flow
│   └── logger.py            # logging setup
├── logs/
│   └── app.log              # auto-created on first run
├── Procfile                 # for Railway deployment
├── main.py                  # entry point + scheduler
├── requirements.txt
├── .env.example             # copy to .env and fill in
└── .env                     # your secrets (never commit this)
```

---

## Cost Breakdown
| Service | Cost |
|---|---|
| Gmail IMAP | Free |
| OpenAI GPT-4o mini | ~$0.001 per summary |
| Twilio WhatsApp | ~$0.005 per message |
| Railway hosting | Free tier (500hrs/month) |
| **Total** | **~$0.006/day** |

---

## Sample Output

```
*OPENAI LAUNCHES GPT-5*
OpenAI released GPT-5 with significantly improved reasoning and multimodal
capabilities. The model outperforms GPT-4 on all major benchmarks and is
available to Plus subscribers immediately.

―――――――――――――――――

*APPLE ACQUIRES AI STARTUP FOR $500M*
Apple quietly acquired Synthesia, a London-based AI video generation startup.
The deal signals Apple's push into generative video ahead of its AR headset
refresh later this year.

―――――――――――――――――

📬 _Full newsletter in your inbox_
```
```