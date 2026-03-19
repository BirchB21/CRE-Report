"""
cre_scraper.py
Commercial Real Estate Market Intelligence — Daily Email Report
Scrapes top CRE news sources, uses Claude AI to analyze each sector,
and emails a black-and-gold HTML report to your Gmail every morning.
"""

import os
import json
import time
import smtplib
import schedule
import requests
import pytz
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List

import anthropic
from bs4 import BeautifulSoup

from email_template import build_html_email


# ─────────────────────────────────────────────────────────────────────────────
# ██  CONFIGURATION  — fill in your credentials here
# ─────────────────────────────────────────────────────────────────────────────

ANTHROPIC_API_KEY  = os.environ.get("ANTHROPIC_API_KEY",  "YOUR_ANTHROPIC_API_KEY")
MODEL              = "claude-opus-4-5"   # swap to "claude-sonnet-4-5" to cut cost ~5x

EMAIL_RECIPIENT    = os.environ.get("EMAIL_TO",           "YOUR_GMAIL@gmail.com")
EMAIL_SENDER       = os.environ.get("EMAIL_FROM",         "YOUR_SENDER@gmail.com")
# Gmail App Password — NOT your normal password
# Get one: Google Account → Security → 2-Step Verification → App Passwords
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "YOUR_16_CHAR_APP_PASSWORD")

SEND_TIME_EST      = "06:00"   # 24-hr format, Eastern Time (auto-adjusts for DST)
OUTPUT_DIR         = "reports"
SAVE_FILES         = True      # also save .md and .json alongside the email

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# ██  CRE SECTORS & NEWS SOURCES
# ─────────────────────────────────────────────────────────────────────────────

CRE_SECTORS = [
    "office", "retail", "industrial",
    "multifamily", "hospitality", "healthcare", "data centers",
]

NEWS_SOURCES = [
    {"name": "GlobeSt",                      "url": "https://www.globest.com/feed/",                  "type": "rss"},
    {"name": "The Real Deal",                 "url": "https://therealdeal.com/feed/",                  "type": "rss"},
    {"name": "Bisnow CRE",                    "url": "https://www.bisnow.com/rss",                     "type": "rss"},
    {"name": "Commercial Property Executive", "url": "https://www.cpexecutive.com/feed/",              "type": "rss"},
    {"name": "Connect CRE",                   "url": "https://www.connectcre.com/feed/",               "type": "rss"},
    {"name": "RE Business Online",            "url": "https://rebusinessonline.com/feed/",             "type": "rss"},
    {"name": "CoStar News",                   "url": "https://www.costar.com/news",                    "type": "html", "selector": "article"},
    {"name": "NAIOP",                         "url": "https://www.naiop.org/Research-and-Publications/Magazine/", "type": "html", "selector": "article"},
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

SECTOR_KEYWORDS = {
    "office":       ["office", "workspace", "coworking", "remote work", "hybrid", "vacancy", "sublease", "downtown"],
    "retail":       ["retail", "store", "shopping center", "mall", "tenant", "brick-and-mortar", "e-commerce", "open-air"],
    "industrial":   ["industrial", "warehouse", "logistics", "distribution", "manufacturing", "fulfillment", "last-mile"],
    "multifamily":  ["multifamily", "apartment", "residential", "rent", "housing", "renter", "cap rate", "BTR"],
    "hospitality":  ["hotel", "hospitality", "lodging", "resort", "airbnb", "STR", "tourism", "RevPAR", "occupancy"],
    "healthcare":   ["healthcare", "medical office", "MOB", "hospital", "senior living", "life sciences", "biotech"],
    "data centers": ["data center", "colocation", "hyperscale", "cloud", "AI infrastructure", "server", "fiber"],
}


# ─────────────────────────────────────────────────────────────────────────────
# ██  SCRAPING
# ─────────────────────────────────────────────────────────────────────────────

def scrape_rss(url: str, name: str) -> List[Dict]:
    articles = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, "xml")
        for item in soup.find_all("item")[:20]:
            title = item.find("title")
            desc  = item.find("description")
            link  = item.find("link")
            date  = item.find("pubDate")
            articles.append({
                "source":      name,
                "title":       title.get_text(strip=True) if title else "",
                "description": BeautifulSoup(desc.get_text(strip=True), "html.parser").get_text(strip=True)[:600] if desc else "",
                "url":         link.get_text(strip=True) if link else "",
                "date":        date.get_text(strip=True) if date else "",
            })
        print(f"  ✓ {name}: {len(articles)} articles")
    except Exception as e:
        print(f"  ✗ {name}: {e}")
    return articles


def scrape_html(url: str, name: str, selector: str) -> List[Dict]:
    articles = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, "html.parser")
        for item in soup.select(selector)[:15]:
            h  = item.find(["h1","h2","h3","h4"])
            a  = item.find("a", href=True)
            ps = item.find_all("p")
            desc = " ".join(p.get_text(strip=True) for p in ps[:2])[:600]
            if h:
                articles.append({
                    "source":      name,
                    "title":       h.get_text(strip=True),
                    "description": desc,
                    "url":         a["href"] if a else url,
                    "date":        datetime.now().strftime("%Y-%m-%d"),
                })
        print(f"  ✓ {name}: {len(articles)} articles")
    except Exception as e:
        print(f"  ✗ {name}: {e}")
    return articles


def scrape_all() -> List[Dict]:
    print("\n📡 Scraping news sources...")
    all_articles = []
    for src in NEWS_SOURCES:
        time.sleep(1)
        if src["type"] == "rss":
            all_articles.extend(scrape_rss(src["url"], src["name"]))
        else:
            all_articles.extend(scrape_html(src["url"], src["name"], src.get("selector","article")))
    print(f"  Total: {len(all_articles)} articles collected")
    return all_articles


def filter_for_sector(articles: List[Dict], sector: str) -> List[Dict]:
    kws = SECTOR_KEYWORDS.get(sector, [sector])
    filtered = [a for a in articles if any(k.lower() in (a["title"]+" "+a["description"]).lower() for k in kws)]
    if len(filtered) < 4:
        general = ["commercial real estate","CRE","cap rate","interest rate","CMBS","REIT","Fed","treasury"]
        for a in articles:
            if a not in filtered and any(k.lower() in (a["title"]+" "+a["description"]).lower() for k in general):
                filtered.append(a)
            if len(filtered) >= 12:
                break
    return filtered[:20]


# ─────────────────────────────────────────────────────────────────────────────
# ██  AI ANALYSIS (Claude)
# ─────────────────────────────────────────────────────────────────────────────

def _articles_block(articles: List[Dict]) -> str:
    return "\n\n".join(
        f"SOURCE: {a['source']}\nTITLE: {a['title']}\nSUMMARY: {a['description']}\nDATE: {a['date']}"
        for a in articles
    )


def ai_top_trends(client: anthropic.Anthropic, articles: List[Dict]) -> str:
    prompt = f"""You are a senior CRE market strategist. Based on today's news, identify the TOP 6 MOST 
IMPORTANT trends or headlines across all commercial real estate sectors.

Format as a numbered list. Each item: ONE concise sentence (max 25 words) that captures why it matters.
Be specific — name markets, figures, or companies where available.

NEWS ARTICLES:
{_articles_block(articles[:40])}

Date: {datetime.now().strftime("%B %d, %Y")}
Return ONLY the numbered list, no preamble."""

    r = client.messages.create(model=MODEL, max_tokens=600,
                                messages=[{"role":"user","content":prompt}])
    return r.content[0].text


def ai_sector_report(client: anthropic.Anthropic, sector: str, articles: List[Dict]) -> str:
    if not articles:
        return f"No significant news found for the {sector.title()} sector today."
    prompt = f"""You are a senior CRE analyst. Write a concise daily briefing for the **{sector.upper()}** 
sector. Use these labeled sections (bold the labels):

**Market Pulse** — 1-2 sentence snapshot
**Key Developments** — 3-4 bullet points of notable news
**Capital & Investment** — financing conditions, notable deals, cap rate movements
**Risks to Watch** — 2-3 bullet points of headwinds
**Quick Take** — one-sentence analyst bottom line

Be specific. Cite sources by name. Keep total under 300 words.

NEWS:
{_articles_block(articles)}

Date: {datetime.now().strftime("%B %d, %Y")}"""

    r = client.messages.create(model=MODEL, max_tokens=700,
                                messages=[{"role":"user","content":prompt}])
    return r.content[0].text


def ai_overall_summary(client: anthropic.Anthropic, sector_reports: Dict[str, str]) -> str:
    snippets = "\n\n".join(f"=== {s.upper()} ===\n{r[:400]}" for s,r in sector_reports.items())
    prompt = f"""Write a 200-word OVERALL CRE MARKET SUMMARY covering:
- The macro CRE environment today
- 2-3 cross-sector themes
- Sector scorecard: rate each sector BULLISH / NEUTRAL / CAUTIOUS with a one-line reason

Bold sector names in the scorecard. Be analytical and direct.

SECTOR REPORTS:
{snippets}

Date: {datetime.now().strftime("%B %d, %Y")}"""

    r = client.messages.create(model=MODEL, max_tokens=500,
                                messages=[{"role":"user","content":prompt}])
    return r.content[0].text


def ai_predictions(client: anthropic.Anthropic, sector_reports: Dict[str, str]) -> str:
    snippets = "\n\n".join(f"=== {s.upper()} ===\n{r[:300]}" for s,r in sector_reports.items())
    prompt = f"""Write a 150-200 word FORWARD OUTLOOK covering:
- 30-day near-term expectations
- Key catalysts / events to watch (Fed, earnings, data releases)
- One contrarian or underappreciated opportunity
- One significant risk that could shift the narrative

Be confident and actionable. Bold key terms.

SECTOR REPORTS:
{snippets}

Date: {datetime.now().strftime("%B %d, %Y")}"""

    r = client.messages.create(model=MODEL, max_tokens=400,
                                messages=[{"role":"user","content":prompt}])
    return r.content[0].text


# ─────────────────────────────────────────────────────────────────────────────
# ██  EMAIL DELIVERY (Gmail SMTP)
# ─────────────────────────────────────────────────────────────────────────────

def send_email(html_body: str, subject: str) -> bool:
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"CRE Intelligence <{EMAIL_SENDER}>"
        msg["To"]      = EMAIL_RECIPIENT

        msg.attach(MIMEText(
            "Your CRE Market Intelligence Report is ready.\n"
            "Please open this email in an HTML-capable client to view the full report.",
            "plain"
        ))
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, GMAIL_APP_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, msg.as_string())

        print(f"  ✓ Email sent → {EMAIL_RECIPIENT}")
        return True

    except smtplib.SMTPAuthenticationError:
        print("  ✗ Gmail authentication failed.")
        print("    → Use a Gmail APP PASSWORD (not your regular password)")
        print("    → Get one at: myaccount.google.com → Security → App Passwords")
        return False
    except Exception as e:
        print(f"  ✗ Email error: {e}")
        return False


# ─────────────────────────────────────────────────────────────────────────────
# ██  OPTIONAL FILE SAVING
# ─────────────────────────────────────────────────────────────────────────────

def save_files(top_trends, sector_reports, overall_summary, predictions, articles):
    date_str = datetime.now().strftime("%Y-%m-%d")

    md_path = os.path.join(OUTPUT_DIR, f"CRE_Report_{date_str}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# CRE Market Intelligence Report\n**{datetime.now().strftime('%B %d, %Y')}**\n\n---\n\n")
        f.write("## 🔥 Top Trends\n\n"); f.write(top_trends); f.write("\n\n---\n\n")
        for sector, report in sector_reports.items():
            f.write(f"## {sector.upper()}\n\n"); f.write(report); f.write("\n\n---\n\n")
        f.write("## Overall Summary\n\n"); f.write(overall_summary); f.write("\n\n---\n\n")
        f.write("## Predictions\n\n"); f.write(predictions); f.write("\n\n")
    print(f"  ✓ Markdown → {md_path}")

    json_path = os.path.join(OUTPUT_DIR, f"CRE_Report_{date_str}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at":   datetime.now().isoformat(),
            "top_trends":     top_trends,
            "sector_reports": sector_reports,
            "overall_summary":overall_summary,
            "predictions":    predictions,
            "article_count":  len(articles),
        }, f, indent=2)
    print(f"  ✓ JSON     → {json_path}")


# ─────────────────────────────────────────────────────────────────────────────
# ██  MAIN REPORT JOB
# ─────────────────────────────────────────────────────────────────────────────

def run_report():
    print("\n" + "═"*60)
    print("  CRE MARKET INTELLIGENCE — DAILY REPORT")
    print(f"  {datetime.now().strftime('%B %d, %Y  |  %I:%M %p')}")
    print("═"*60)

    articles = scrape_all()
    if not articles:
        print("\n⚠️  No articles collected. Aborting.")
        return

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    print("\n🤖 Running AI analysis...")

    print("  → Top trends...")
    top_trends = ai_top_trends(client, articles)
    time.sleep(0.5)

    sector_reports = {}
    for sector in CRE_SECTORS:
        print(f"  → {sector.upper()}...")
        sector_reports[sector] = ai_sector_report(client, sector, filter_for_sector(articles, sector))
        time.sleep(0.5)

    print("  → Overall summary...")
    overall_summary = ai_overall_summary(client, sector_reports)
    time.sleep(0.5)

    print("  → Predictions...")
    predictions = ai_predictions(client, sector_reports)

    print("\n📧 Building & sending email...")
    html_body = build_html_email(top_trends, sector_reports, overall_summary, predictions)
    subject   = f"📊 CRE Market Intelligence — {datetime.now().strftime('%B %d, %Y')}"
    send_email(html_body, subject)

    if SAVE_FILES:
        print("\n💾 Saving report files...")
        save_files(top_trends, sector_reports, overall_summary, predictions, articles)

    print("\n" + "═"*60)
    print("  ✅ DONE")
    print("═"*60 + "\n")


# ─────────────────────────────────────────────────────────────────────────────
# ██  SCHEDULER
# ─────────────────────────────────────────────────────────────────────────────

def start_scheduler():
    eastern = pytz.timezone("America/New_York")
    now_e   = datetime.now(eastern)
    h, m    = map(int, SEND_TIME_EST.split(":"))
    target  = now_e.replace(hour=h, minute=m, second=0, microsecond=0)
    utc_str = target.astimezone(pytz.utc).strftime("%H:%M")

    print(f"\n⏰  Scheduler active — daily at {SEND_TIME_EST} EST ({utc_str} UTC)")
    print("    Press Ctrl+C to stop.\n")

    schedule.every().day.at(utc_str).do(run_report)
    while True:
        schedule.run_pending()
        time.sleep(30)


# ─────────────────────────────────────────────────────────────────────────────
# ██  ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    if "--now" in sys.argv:
        run_report()          # python cre_scraper.py --now  → run immediately
    else:
        start_scheduler()     # python cre_scraper.py        → wait for 6 AM EST
