import os
import json
import smtplib
import ssl
from datetime import datetime, timezone, timedelta
from email.message import EmailMessage

KST = timezone(timedelta(hours=9))
WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]


def load_events():
    with open("schedule.json", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("events", [])


def todays_events(events):
    today = datetime.now(KST).strftime("%Y-%m-%d")
    todays = [e for e in events if e.get("date") == today]
    todays.sort(key=lambda e: e.get("time", ""))
    return today, todays


def build_message(today, events):
    d = datetime.strptime(today, "%Y-%m-%d")
    dow = WEEKDAYS[d.weekday()]
    subject = f"[일정] {today} ({dow}) 오늘 일정 {len(events)}건"

    lines = [f"{today} ({dow}) 오늘의 일정", ""]
    if not events:
        lines.append("오늘 등록된 일정이 없습니다.")
    else:
        for e in events:
            t = e.get("time", "")
            title = e.get("title", "")
            memo = e.get("memo", "")
            line = f"• {t}  {title}"
            if memo:
                line += f"  — {memo}"
            lines.append(line)
    return subject, "\n".join(lines)


def send_mail(subject, body):
    user = os.environ["MAIL_USERNAME"]
    pw = os.environ["MAIL_PASSWORD"]
    to = os.environ["MAIL_TO"]

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to
    msg.set_content(body)

    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as server:
        server.login(user, pw)
        server.send_message(msg)


def main():
    events = load_events()
    today, todays = todays_events(events)
    subject, body = build_message(today, todays)
    send_mail(subject, body)
    print(f"sent: {subject}")


if __name__ == "__main__":
    main()
