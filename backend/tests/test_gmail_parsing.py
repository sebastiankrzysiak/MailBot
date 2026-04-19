import base64
import pytest
from unittest.mock import MagicMock, patch


def make_message(subject="Test Subject", sender="John Doe <john@example.com>",
                 date="Mon, 1 Jan 2024 10:00:00 -0500", body_text="Hello world"):
    encoded = base64.urlsafe_b64encode(body_text.encode()).decode()
    return {
        "id": "msg123",
        "payload": {
            "headers": [
                {"name": "Subject", "value": subject},
                {"name": "From", "value": sender},
                {"name": "Date", "value": date},
            ],
            "parts": [
                {"mimeType": "text/plain", "body": {"data": encoded}}
            ]
        }
    }


def parse_email(msg):
    headers = msg["payload"]["headers"]
    subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
    sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown")
    date = next((h["value"] for h in headers if h["name"] == "Date"), "")

    if " -" in date:
        date = date.split(" -")[0]
    if " +" in date:
        date = date.split(" +")[0]

    body = ""
    if "parts" in msg["payload"]:
        for part in msg["payload"]["parts"]:
            if part["mimeType"] == "text/plain":
                body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
                break

    return {"id": msg["id"], "subject": subject, "sender": sender, "date": date, "body": body[:500]}


def test_parses_subject():
    msg = make_message(subject="Hello from pytest")
    email = parse_email(msg)
    assert email["subject"] == "Hello from pytest"


def test_parses_sender():
    msg = make_message(sender="Jane <jane@example.com>")
    email = parse_email(msg)
    assert email["sender"] == "Jane <jane@example.com>"


def test_strips_timezone_minus():
    msg = make_message(date="Mon, 1 Jan 2024 10:00:00 -0500")
    email = parse_email(msg)
    assert "-0500" not in email["date"]
    assert "10:00:00" in email["date"]


def test_strips_timezone_plus():
    msg = make_message(date="Mon, 1 Jan 2024 10:00:00 +0000")
    email = parse_email(msg)
    assert "+0000" not in email["date"]


def test_decodes_body():
    msg = make_message(body_text="This is the email body.")
    email = parse_email(msg)
    assert email["body"] == "This is the email body."


def test_body_truncated_to_500():
    long_body = "x" * 1000
    msg = make_message(body_text=long_body)
    email = parse_email(msg)
    assert len(email["body"]) == 500


def test_fallback_subject():
    msg = make_message()
    msg["payload"]["headers"] = [h for h in msg["payload"]["headers"] if h["name"] != "Subject"]
    email = parse_email(msg)
    assert email["subject"] == "No Subject"


def test_no_body_parts():
    msg = {
        "id": "abc",
        "payload": {
            "headers": [
                {"name": "Subject", "value": "Hi"},
                {"name": "From", "value": "a@b.com"},
                {"name": "Date", "value": "Mon, 1 Jan 2024"},
            ]
        }
    }
    email = parse_email(msg)
    assert email["body"] == ""
