"""
send_nudge.py — Weekly progress-nudge email (scaffold)
======================================================
Composes a short "here's what to learn next" email and (optionally) sends it via
SendGrid. Wired to a weekly GitHub Actions cron (.github/workflows/nudge.yml).

It is SAFE by default: with no credentials it does a DRY RUN (prints the email,
sends nothing). To actually send, add these as GitHub repo secrets:
    SENDGRID_API_KEY   your SendGrid API key
    NUDGE_TO           recipient email
    NUDGE_FROM         a verified SendGrid sender email
optionally NUDGE_NAME / NUDGE_ROLE / NUDGE_MATCH / NUDGE_SKILLS to personalise.

TODO (next step): instead of the single env-driven recipient below, loop over
real users by reading progress from the SkillBridge backend API and email each.
"""

import os
import sys

APP_URL = "https://skillbridge-darshan.streamlit.app/"


def compose_nudge(name: str, role: str, match_percent: int, next_skills) -> str:
    """Build the plain-text nudge body (pure + unit-tested)."""
    who = (name or "").strip() or "there"
    nxt = ", ".join(list(next_skills)[:3]) if next_skills else "your next skill"
    return (
        f"Hi {who},\n\n"
        f"You're {int(match_percent)}% ready for {role}. "
        f"This week, focus on: {nxt}.\n\n"
        f"Open SkillBridge to tick off what you've learned and watch your score climb:\n"
        f"{APP_URL}\n\n"
        "Keep going — you've got this.\n— SkillBridge"
    )


def send_email_sendgrid(api_key, to_email, from_email, subject, body):
    """Send one email via SendGrid's HTTP API. Returns (status_code, text)."""
    import requests
    resp = requests.post(
        "https://api.sendgrid.com/v3/mail/send",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "personalizations": [{"to": [{"email": to_email}]}],
            "from": {"email": from_email},
            "subject": subject,
            "content": [{"type": "text/plain", "value": body}],
        },
        timeout=30,
    )
    return resp.status_code, resp.text


def main():
    api_key = os.environ.get("SENDGRID_API_KEY", "")
    to_email = os.environ.get("NUDGE_TO", "")
    from_email = os.environ.get("NUDGE_FROM", "")

    body = compose_nudge(
        os.environ.get("NUDGE_NAME", "there"),
        os.environ.get("NUDGE_ROLE", "your target role"),
        int(os.environ.get("NUDGE_MATCH", "0") or 0),
        [s.strip() for s in os.environ.get("NUDGE_SKILLS", "").split(",") if s.strip()],
    )
    subject = "Your weekly SkillBridge nudge"

    if not (api_key and to_email and from_email):
        print("DRY RUN — set SENDGRID_API_KEY, NUDGE_TO and NUDGE_FROM to actually send.\n")
        print("Subject:", subject)
        print(body)
        return 0

    code, text = send_email_sendgrid(api_key, to_email, from_email, subject, body)
    print("SendGrid status:", code)
    if code >= 400:
        print(text[:300])
        return 1
    print("Nudge sent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
