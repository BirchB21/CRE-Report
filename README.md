# 📊 CRE Market Intelligence — Daily Email Report

Scrapes commercial real estate news daily, runs it through Claude AI, and emails you a **black-and-gold HTML briefing** at 6:00 AM EST covering every major CRE sector.

---

## 📬 What You Get Each Morning

```
Subject: 📊 CRE Market Intelligence — March 19, 2026
```

The email is structured as:

| Section | Content |
|---|---|
| 🔥 **Top Trends** | Numbered list of the 6 most important CRE stories today |
| 🏢 **Office** | Market pulse, key developments, capital markets, risks |
| 🛍️ **Retail** | Same structure |
| 🏭 **Industrial** | Same structure |
| 🏠 **Multifamily** | Same structure |
| 🏨 **Hospitality** | Same structure |
| 🏥 **Healthcare** | Same structure |
| 💻 **Data Centers** | Same structure |
| 📋 **Overall Summary** | Cross-sector synthesis + sector scorecard |
| 🔭 **Predictions** | 30-day outlook, catalysts, risks, opportunities |

---

## 🚀 Setup (5 minutes)

### Step 1 — Install Python dependencies
```bash
pip install -r requirements.txt
```

### Step 2 — Get a Gmail App Password

> ⚠️ You **cannot** use your regular Gmail password. Google requires an App Password for SMTP automation.

1. Go to [myaccount.google.com](https://myaccount.google.com)
2. **Security** → **2-Step Verification** (must be enabled first)
3. Scroll down → **App Passwords**
4. Select app: **Mail** | Select device: **Other (Custom name)** → name it "CRE Bot"
5. Copy the 16-character password generated (e.g. `abcd efgh ijkl mnop`)

### Step 3 — Configure credentials

**Option A — Environment variables (most secure, recommended):**
```bash
# Mac / Linux
export ANTHROPIC_API_KEY="sk-ant-..."
export EMAIL_TO="yourname@gmail.com"
export EMAIL_FROM="yourname@gmail.com"
export GMAIL_APP_PASSWORD="abcdefghijklmnop"

# Windows PowerShell
$env:ANTHROPIC_API_KEY="sk-ant-..."
$env:EMAIL_TO="yourname@gmail.com"
$env:EMAIL_FROM="yourname@gmail.com"
$env:GMAIL_APP_PASSWORD="abcdefghijklmnop"
```

**Option B — Edit the script directly:**

Open `cre_scraper.py` and fill in the four config values at the top of the file:
```python
ANTHROPIC_API_KEY  = "sk-ant-..."
EMAIL_RECIPIENT    = "yourname@gmail.com"
EMAIL_SENDER       = "yourname@gmail.com"
GMAIL_APP_PASSWORD = "abcdefghijklmnop"
```

---

## ▶️ Running the Script

### Test it immediately (don't wait for 6 AM):
```bash
python cre_scraper.py --now
```

### Start the daily scheduler (runs every day at 6:00 AM EST):
```bash
python cre_scraper.py
```
Leave this terminal open (or run it as a background service — see below).

---

## ⏰ Keeping It Running 24/7

### Mac/Linux — run as a background process
```bash
nohup python cre_scraper.py > cre_scraper.log 2>&1 &
echo "PID: $!"
```
To stop it: `kill <PID>`

### Mac — launchd (runs at login, restarts automatically)
Create `~/Library/LaunchAgents/com.cre.scraper.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.cre.scraper</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/python3</string>
    <string>/path/to/cre_scraper.py</string>
  </array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>/tmp/cre_scraper.log</string>
</dict>
</plist>
```
```bash
launchctl load ~/Library/LaunchAgents/com.cre.scraper.plist
```

### Windows — Task Scheduler
1. Open **Task Scheduler** → **Create Basic Task**
2. Trigger: **Daily**, start time: `5:50 AM` (gives a 10-min buffer)
3. Action: **Start a program** → `python` → Arguments: `C:\path\to\cre_scraper.py`

### GitHub Actions (100% free, cloud-hosted, no computer needed)
Create `.github/workflows/daily_report.yml`:
```yaml
name: Daily CRE Report
on:
  schedule:
    - cron: '0 11 * * *'  # 11:00 UTC = 6:00 AM EST (adjust for EDT: use '0 10 * * *')
jobs:
  report:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: '3.11'}
      - run: pip install -r requirements.txt
      - run: python cre_scraper.py --now
        env:
          ANTHROPIC_API_KEY:  ${{ secrets.ANTHROPIC_API_KEY }}
          EMAIL_TO:           ${{ secrets.EMAIL_TO }}
          EMAIL_FROM:         ${{ secrets.EMAIL_FROM }}
          GMAIL_APP_PASSWORD: ${{ secrets.GMAIL_APP_PASSWORD }}
```
Add all four secrets in: **GitHub repo → Settings → Secrets → Actions**

---

## 💰 Estimated Cost Per Run

| Model | Calls | Approx. Cost |
|---|---|---|
| `claude-opus-4-5` (best quality) | ~10 | $0.35 – $0.65 |
| `claude-sonnet-4-5` (cost-efficient) | ~10 | $0.05 – $0.12 |

Change `MODEL` in `cre_scraper.py` to switch.

At daily cadence: **Opus ≈ $10–20/month | Sonnet ≈ $1.50–4/month**

---

## 🔧 Customization

| What | Where |
|---|---|
| Add/remove sectors | `CRE_SECTORS` list in `cre_scraper.py` |
| Add news sources | `NEWS_SOURCES` list |
| Add sector keywords | `SECTOR_KEYWORDS` dict |
| Change send time | `SEND_TIME_EST = "06:00"` |
| Turn off file saving | `SAVE_FILES = False` |
| Change report depth | Adjust `max_tokens` in each `ai_*` function |

---

## 📁 File Structure

```
cre-market-scraper/
├── cre_scraper.py       ← main script (run this)
├── email_template.py    ← HTML email builder (black & gold design)
├── requirements.txt     ← Python dependencies
├── README.md            ← this file
└── reports/             ← auto-created; daily .md and .json archives
```
