# UAE Software Engineer Job Alert

Polls UAE employers + LinkedIn every 10 minutes via GitHub Actions and emails new
matching jobs to `riajal97@gmail.com`. The goal is "first to apply" recency.

## What it does

Every 10 minutes a GitHub Actions cron:
1. Hits each company's ATS JSON endpoint (Greenhouse / Lever / Ashby / Workday).
2. Best-effort hits LinkedIn via `python-jobspy` (works ~70% of runs from Actions IPs — failures are swallowed).
3. Filters titles + locations to UAE SWE roles (config in `config.yml`).
4. Skips anything previously emailed (`state.json`).
5. Sends an HTML email digest via Gmail SMTP.
6. Commits the updated `state.json` back to the repo.

If no new jobs match, no email is sent — silence means "no new jobs."

## One-time setup

### 1. GitHub repo

```bash
cd ~/ria_workspace/dubai/jobs
git init && git add . && git commit -m "initial"
gh repo create dubai-jobs --private --source=. --push
```

### 2. Gmail App Password

1. Enable 2FA on `riajal97@gmail.com`: https://myaccount.google.com/security
2. Generate app password: https://myaccount.google.com/apppasswords
3. Add as repo secrets:
   ```bash
   gh secret set GMAIL_USER --body "riajal97@gmail.com"
   gh secret set GMAIL_APP_PASSWORD --body "<16-char-app-password>"
   ```

### 3. Discover each company's ATS

`companies.yml` ships with Careem already wired up. For every other company
listed with `ats: TBD`, run the discovery script and paste the result back:

```bash
python scripts/discover_ats.py https://careers.talabat.com --name Talabat
```

If the script can't detect anything from the main careers page, open the page
in a browser, click through to the actual job board, and re-run with that URL.
For Workday companies you'll also need to open Chrome devtools, search for any
role, and copy the exact POST endpoint from the Network tab.

### 4. Smoke-test locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
GMAIL_USER=riajal97@gmail.com GMAIL_APP_PASSWORD=<app-pw> python -m src.main
```

The first run will email every currently-open UAE SWE role across all configured
employers — treat this as the "initial dump."

### 5. Enable the cron

After the first successful local run, push and trigger the workflow once:

```bash
gh workflow run "Poll UAE jobs"
gh run watch
```

From then on it runs every 10 minutes automatically.

## Adding a new company

1. `python scripts/discover_ats.py <careers_url> --name "Company"`
2. Paste the printed YAML block under `companies:` in `companies.yml`
3. Commit + push — next cron picks it up.

## Adjusting filters

Edit `config.yml`. Title and location lists are case-insensitive substring
matches. Anything in `title_exclude` is a hard veto.

## Why some sources aren't here

Indeed UAE, Bayt, and Wellfound all sit behind Cloudflare / DataDome / PerimeterX
which reliably block GitHub Actions runners (Azure datacenter IPs). Indeed's
RSS feeds were also discontinued. Adding them would require a paid scraper API
(~$50/mo) — not worth it given the ATS endpoints cover the same employers.
