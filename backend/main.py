import time
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from gmail import get_recent_emails, get_gmail_service
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

cache = {}

client = OpenAI(
    base_url="http://192.168.1.31:1234/v1",
    api_key="lm-studio"
)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "DELETE"],
    allow_headers=["*"],
)

@app.get("/summarize")
def summarize(max_results: int = 100):
    summaries = []
    email_list = get_recent_emails(max_results=max_results)
    total_start = time.perf_counter()

    for email in email_list:
        sender = email["sender"]
        if "<" in sender:
            sender = sender.split(" <")[0]
            if sender[0] == "\"" and sender[-1] == "\"":
                sender = sender[1:-1]

        if email["id"] in cache:
            summaries.append({
                "id": email["id"],
                "subject": email["subject"],
                "sender": sender,
                "date": email["date"],
                "summary": cache[email["id"]]
            })
            continue

        email_start = time.perf_counter()

        response = client.chat.completions.create(
            extra_body={"thinking": {"type": "disabled"}},
            model="meta-llama-3.1-8b-instruct",
            messages=[{"role": "user", "content": f"Summarize this email in exactly 2 sentences. Do not include any preamble, introduction, or URLs in your summary, just the summary itself. Subject: {email['subject']} Body: {email['body']}"}]
        )

        elapsed = time.perf_counter() - email_start
        print(f"[{elapsed:.2f}s] {email['subject']!r}")

        cache[email["id"]] = response.choices[0].message.content
        summaries.append({
            "id": email["id"],
            "subject": email["subject"],
            "sender": sender,
            "date": email["date"],
            "summary": response.choices[0].message.content
        })

    print(f"[{time.perf_counter() - total_start:.2f}s] Total — {len(summaries)} emails")
    return summaries

@app.get("/recurring")
def recurring(max_results: int = 100):
    email_list = get_recent_emails(max_results=max_results)
    sender_to_emails = defaultdict(list)

    for email in email_list:
        sender = email["sender"]

        if "<" in sender:
            sender = sender.split("<")[1].split(">")[0]

        if "@" not in sender:
            continue

        _, domain = sender.split("@", 1)

        sender_to_emails[domain].append({"id": email["id"], "subject": email["subject"]})

    return [{"sender": k, "count": len(v), "emails": v} for k, v in sorted(sender_to_emails.items(), key=lambda item: len(item[1]), reverse=True)]

@app.delete("/emails/{email_id}")
def delete_email(email_id: str):
    service = get_gmail_service()
    service.users().messages().trash(userId="me", id=email_id).execute()
    return {"status": "trashed"}

@app.get("/jobs")
def jobs(max_results: int = 100):
    email_list = get_recent_emails(max_results=max_results)
    summaries = []
    keywords = [
        "interview", "assessment", "codesignal", "hackerrank", "schedule",
        "zoom", "phone screen", "take-home", "coding challenge", "onsite",
        "technical screen", "offer letter", "start date", "calendar invite",
        "availability", "time slot", "reschedule", "confirm your interview",
        "book a time", "calendly", "hiring manager", "panel interview",
        "final round", "second round", "third round", "loop", "behavioral",
        "system design", "culture fit", "reference check", "codility",
        "leetcode", "greenhouse", "lever", "workday", "google meet", "webex",
        "teams", "move forward", "next steps", "pleased to inform",
        "we'd like to", "congratulations", "background check", "compensation",
        "salary", "benefits", "onboarding", "welcome", "day one", "equipment"
    ]

    negative_keywords = ["unfortunately", "not moving forward", "not selected"]
    for email in email_list:
        text = (email['subject'] + email['body']).lower()
        if any(word in text for word in negative_keywords):
            continue
        found = any(word in text for word in keywords)
        if found:
            response = client.chat.completions.create(
                extra_body={"thinking": {"type": "disabled"}},
                model="meta-llama-3.1-8b-instruct",
                messages=[
                    {
                        "role": "user",
                        "content": (
                            "You are a job search assistant that extracts actionable information from emails. "
                            "Be concise and direct. Never include URLs, greetings, or filler phrases.\n\n"
                            "Classify and summarize the following job-related email.\n\n"
                            "If the email is a rejection, a thank-you-for-applying confirmation, or an automated "
                            "acknowledgment that an application was received, respond with only the word SKIP.\n\n"
                            "Otherwise, summarize in exactly 2 sentences. Focus only on: next steps, deadlines, "
                            "interview details, or assessment instructions. Do not repeat the subject or include any preamble.\n\n"
                            f"Subject: {email['subject']}\n"
                            f"Body: {email['body']}"
                        )
                    }
                ]
            )

            content = response.choices[0].message.content
            if "SKIP" not in content.strip().upper():
                sender = email["sender"]
                if "<" in sender:
                    sender = sender.split(" <")[0]
                    if sender[0] == "\"" and sender[-1] == "\"":
                        sender = sender[1:-1]

                cache[email["id"]] = content
                summaries.append({
                    "id": email["id"],
                    "subject": email["subject"],
                    "sender": sender,
                    "date": email["date"],
                    "summary": content
                })

    return summaries

@app.get("/school")
def school(max_results: int = 100):
    school_email = os.getenv("SCHOOL_EMAIL")
    email_list = get_recent_emails(max_results=max_results, query=f"to:{school_email} in:anywhere")
    summaries = []

    for email in email_list:
        sender = email["sender"]
        if "<" in sender:
            sender = sender.split(" <")[0]
            if sender[0] == "\"" and sender[-1] == "\"":
                sender = sender[1:-1]

        if email["id"] in cache:
            summaries.append({
                "id": email["id"],
                "subject": email["subject"],
                "sender": sender,
                "date": email["date"],
                "summary": cache[email["id"]]
            })
            continue

        response = client.chat.completions.create(
            extra_body={"thinking": {"type": "disabled"}},
            model="meta-llama-3.1-8b-instruct",
            messages=[{"role": "user", "content": f"Summarize this email in exactly 2 sentences. Do not include any preamble, introduction, or URLs in your summary, just the summary itself. Subject: {email['subject']} Body: {email['body']}"}]
        )

        cache[email["id"]] = response.choices[0].message.content
        summaries.append({
            "id": email["id"],
            "subject": email["subject"],
            "sender": sender,
            "date": email["date"],
            "summary": response.choices[0].message.content
        })

    return summaries
