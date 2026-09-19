# Gmail Bulk Email Sender

A simple, single-file Python script for sending personalized bulk emails
through **Gmail SMTP** using an **App Password**. Includes dry-run mode,
per-recipient message count, rate limiting, and dual logging.

[![Python 3.7+](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ⚠️ Read This First

Sending bulk email through a personal Gmail account has **strict limits**
and **real consequences** if misused:

- **Gmail limits:** ~500 recipients/day (personal), ~2000/day (Workspace)
- **Account risk:** Unsolicited bulk mail can get your Gmail **suspended**
- **Legal risk:** CAN-SPAM, GDPR, CASL and similar laws apply to bulk mail
- **Privacy:** Your Gmail address is visible to every recipient

This tool is intended for **small, opted-in lists** (a club, a class, a
small newsletter). If you need sender privacy or higher volume, use a
transactional email service instead (Brevo, SendGrid, Mailgun, SES).

---

## Features

- 📧 **Personalized bulk emails** via a single template
- 🧪 **Dry-run mode by default** — preview before sending anything
- 🔁 **Per-recipient message count** — send N copies to the same address
- ⏱️ **Rate limiting** — configurable delay between sends
- 📝 **Dual logging** — console + `bulk_email_log.txt`
- 🔑 **No hardcoded secrets** — credentials come from environment variables
- 🐍 **Standard library only** — no `pip install` required

---

## Quick Start

### 1. Create a Gmail App Password

1. Enable **2-Step Verification** on your Google account:
   https://myaccount.google.com/security
2. Create an **App Password**:
   https://myaccount.google.com/apppasswords
3. Copy the 16-character password (looks like `abcd efgh ijkl mnop`)

> ⚠️ Your regular Gmail password will **not** work with `smtplib`.

### 2. Clone and configure

```bash
git clone https://github.com/YOUR_USERNAME/gmail-bulk-email-sender.git
cd gmail-bulk-email-sender
```

Set environment variables:

**Linux / macOS:**
```bash
export GMAIL_ADDRESS="you@gmail.com"
export GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"
```

**Windows (PowerShell):**
```powershell
$env:GMAIL_ADDRESS="you@gmail.com"
$env:GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"
```

Or copy `.env.example` to `.env` and fill it in.

### 3. Edit recipients and content

Open `bulk_email_sender.py` and edit:

```python
RECIPIENTS = [
    {"email": "alex@example.com", "name": "Alex", "count": 1},
    {"email": "sam@example.com", "name": "Sam", "count": 2},
]

SUBJECT = "Your subject here"
BODY_TEMPLATE = """Hi {name}, ..."""
```

### 4. Dry run, then send

```bash
python bulk_email_sender.py       # DRY_RUN = True by default
```

When satisfied, set `DRY_RUN = False` and run again.

---

## Configuration Reference

### Environment Variables

| Variable | Required | Example |
|---|---|---|
| `GMAIL_ADDRESS` | Yes | `you@gmail.com` |
| `GMAIL_APP_PASSWORD` | Yes | `abcd efgh ijkl mnop` |

### In-File Constants

| Constant | Default | Purpose |
|---|---|---|
| `SMTP_SERVER` | `smtp.gmail.com` | Gmail SMTP host |
| `SMTP_PORT` | `587` | STARTTLS port |
| `DELAY_BETWEEN_EMAILS_SECONDS` | `2` | Delay between sends |
| `DRY_RUN` | `True` | Safety switch |
| `LOG_FILE` | `bulk_email_log.txt` | Log output path |

### Recipient Schema

```python
{"email": "user@example.com", "name": "Alex", "count": 1}
```

| Key | Required | Default | Notes |
|---|---|---|---|
| `email` | Yes | — | Recipient address |
| `name` | No | `""` | Falls back to `"there"` in body |
| `count` | No | `1` | Number of copies to send |

---

## How It Works

```
┌──────────────────┐  STARTTLS  ┌─────────────────┐         ┌──────────────┐
│  bulk_email_     │ ─────────► │  Gmail SMTP     │ ──────► │  Recipient   │
│  sender.py       │            │  smtp.gmail.com │         │  inbox       │
└──────────────────┘            └─────────────────┘         └──────────────┘
        │
        │ From: you@gmail.com    ← your address is visible
        ▼
```

The script:
1. Loads credentials from environment variables
2. Builds a personalized `MIMEMultipart` message per recipient
3. Opens a TLS connection to Gmail's SMTP server
4. Authenticates with your App Password
5. Sends each message sequentially with a configurable delay
6. Logs every success and failure

---

## Responsible Use ⚠️

This tool sends real email. **Misuse can get your Google account
suspended and may violate anti-spam laws.**

By using this tool you agree to:

- ✅ Only email people who **opted in** to receive your mail
- ✅ Always include a **clear unsubscribe** method
- ✅ Respect **Gmail's daily limits**
- ✅ Comply with **anti-spam laws** in your jurisdiction
- ❌ **Not** send unsolicited bulk mail
- ❌ **Not** use purchased or scraped email lists

The author is not responsible for misuse.

---

## FAQ

**Q: Why doesn't my regular Gmail password work?**
A: Google blocks plain-password SMTP for security. You must use an
**App Password**, which requires 2-Step Verification to be enabled.

**Q: How many emails can I send per day?**
A: Roughly 500/day for personal Gmail, ~2000/day for Google Workspace.
Each copy counts toward the limit.

**Q: Will recipients see my Gmail address?**
A: Yes. Gmail stamps the authenticated account in the `From:` and
`Return-Path` headers. To hide it, use a transactional service instead.

**Q: Can I send HTML emails?**
A: Not currently — plain text only. Swap `MIMEText(body, "plain")` for
`MIMEText(body, "html")` and write HTML in `BODY_TEMPLATE`.

**Q: Can I load recipients from a CSV file?**
A: Not yet — see [Roadmap](#roadmap). For now, edit the `RECIPIENTS` list.

---

## Roadmap

- [ ] Load recipients from CSV / JSON
- [ ] HTML email support
- [ ] Attachment support
- [ ] Unsubscribe link + `List-Unsubscribe` header
- [ ] Resume-after-crash (skip already-sent recipients)
- [ ] `--dry-run` and `--config` CLI flags
- [ ] Optional transactional provider backends
