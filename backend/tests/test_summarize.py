import pytest
from unittest.mock import MagicMock, patch


def strip_sender_quotes(sender):
    if "<" in sender:
        sender = sender.split(" <")[0]
        if sender[0] == '"' and sender[-1] == '"':
            sender = sender[1:-1]
    return sender


def build_summary(email, cache, llm_client):
    sender = strip_sender_quotes(email["sender"])

    if email["id"] in cache:
        return {
            "id": email["id"],
            "subject": email["subject"],
            "sender": sender,
            "date": email["date"],
            "summary": cache[email["id"]],
            "from_cache": True,
        }

    response = llm_client.chat.completions.create(
        model="meta-llama-3.1-8b-instruct",
        messages=[{"role": "user", "content": f"Summarize: {email['body']}"}]
    )
    content = response.choices[0].message.content
    cache[email["id"]] = content
    return {
        "id": email["id"],
        "subject": email["subject"],
        "sender": sender,
        "date": email["date"],
        "summary": content,
        "from_cache": False,
    }


def make_email(id="msg1", sender="Sender <sender@example.com>", subject="Sub", body="Body", date="Jan 1"):
    return {"id": id, "sender": sender, "subject": subject, "body": body, "date": date}


def make_llm_client(response_text="A short summary."):
    client = MagicMock()
    client.chat.completions.create.return_value.choices[0].message.content = response_text
    return client


def test_uses_cache_when_available():
    email = make_email(id="cached")
    cache = {"cached": "Cached summary."}
    client = make_llm_client()

    result = build_summary(email, cache, client)

    assert result["summary"] == "Cached summary."
    assert result["from_cache"] is True
    client.chat.completions.create.assert_not_called()


def test_calls_llm_on_cache_miss():
    email = make_email(id="new_id")
    cache = {}
    client = make_llm_client("LLM generated summary.")

    result = build_summary(email, cache, client)

    assert result["summary"] == "LLM generated summary."
    assert result["from_cache"] is False
    client.chat.completions.create.assert_called_once()


def test_stores_result_in_cache_after_llm():
    email = make_email(id="new_id")
    cache = {}
    client = make_llm_client("Stored summary.")

    build_summary(email, cache, client)

    assert cache["new_id"] == "Stored summary."


def test_strips_quoted_display_name():
    email = make_email(sender='"Company Name" <noreply@company.com>')
    result = build_summary(email, {}, make_llm_client())
    assert result["sender"] == "Company Name"


def test_strips_unquoted_display_name():
    email = make_email(sender="Jane Doe <jane@example.com>")
    result = build_summary(email, {}, make_llm_client())
    assert result["sender"] == "Jane Doe"


def test_sender_without_angle_brackets():
    email = make_email(sender="raw@example.com")
    result = build_summary(email, {}, make_llm_client())
    assert result["sender"] == "raw@example.com"


def test_summary_fields_present():
    email = make_email()
    result = build_summary(email, {}, make_llm_client())
    for key in ("id", "subject", "sender", "date", "summary"):
        assert key in result
