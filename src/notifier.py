import os
import smtplib
from datetime import datetime, timezone
from email.message import EmailMessage

from jinja2 import Template

from src.sources import Job

_HTML = Template("""<!doctype html>
<html><body style="font-family:-apple-system,BlinkMacSystemFont,Helvetica,Arial,sans-serif;color:#222;">
<h2 style="margin-bottom:4px;">{{ jobs|length }} new UAE software engineer {{ 'job' if jobs|length == 1 else 'jobs' }}</h2>
<p style="color:#888;margin-top:0;font-size:13px;">{{ generated_at }}</p>
<table cellpadding="8" cellspacing="0" border="0" style="border-collapse:collapse;width:100%;">
  <thead><tr style="background:#f4f4f4;text-align:left;">
    <th>Role</th><th>Company</th><th>Location</th><th>Posted</th><th>Source</th><th></th>
  </tr></thead>
  <tbody>
  {% for j in jobs %}
    <tr style="border-bottom:1px solid #eee;">
      <td><strong>{{ j.title }}</strong></td>
      <td>{{ j.company }}</td>
      <td>{{ j.location }}</td>
      <td>{{ j.posted_at or '-' }}</td>
      <td style="color:#888;">{{ j.source }}</td>
      <td><a href="{{ j.url }}" style="background:#1a73e8;color:#fff;padding:6px 12px;text-decoration:none;border-radius:4px;">Apply &rarr;</a></td>
    </tr>
  {% endfor %}
  </tbody>
</table>
<p style="color:#aaa;font-size:12px;margin-top:24px;">UAE job alert bot &middot; <a href="https://github.com/{{ repo or '' }}" style="color:#aaa;">repo</a></p>
</body></html>
""")


def send_digest(jobs: list[Job], sender: str, recipient: str) -> None:
    if not jobs:
        return

    user = os.environ["GMAIL_USER"]
    password = os.environ["GMAIL_APP_PASSWORD"]
    repo = os.environ.get("GITHUB_REPOSITORY", "")

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    html = _HTML.render(jobs=jobs, generated_at=generated_at, repo=repo)
    text = "\n\n".join(
        f"{j.title} @ {j.company} ({j.location})\n  posted: {j.posted_at or '-'}\n  {j.url}"
        for j in jobs
    )

    msg = EmailMessage()
    msg["Subject"] = f"\U0001F514 {len(jobs)} new UAE SWE job{'s' if len(jobs) > 1 else ''} ({generated_at})"
    msg["From"] = sender
    msg["To"] = recipient
    msg.set_content(text)
    msg.add_alternative(html, subtype="html")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(user, password)
        smtp.send_message(msg)
