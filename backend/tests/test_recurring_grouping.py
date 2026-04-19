from collections import defaultdict


def group_by_domain(email_list):
    sender_to_emails = defaultdict(list)
    for email in email_list:
        sender = email["sender"]
        if "<" in sender:
            sender = sender.split("<")[1].split(">")[0]
        if "@" not in sender:
            continue
        _, domain = sender.split("@", 1)
        sender_to_emails[domain].append({"id": email["id"], "subject": email["subject"]})

    return [
        {"sender": k, "count": len(v), "emails": v}
        for k, v in sorted(sender_to_emails.items(), key=lambda item: len(item[1]), reverse=True)
    ]


def make_email(id, sender, subject="Subject"):
    return {"id": id, "sender": sender, "subject": subject, "body": "", "date": ""}


def test_groups_by_domain():
    emails = [
        make_email("1", "newsletter@example.com"),
        make_email("2", "promo@example.com"),
        make_email("3", "info@other.com"),
    ]
    result = group_by_domain(emails)
    domains = [r["sender"] for r in result]
    assert "example.com" in domains
    assert "other.com" in domains


def test_count_matches_emails():
    emails = [
        make_email("1", "a@foo.com"),
        make_email("2", "b@foo.com"),
        make_email("3", "c@foo.com"),
    ]
    result = group_by_domain(emails)
    assert result[0]["sender"] == "foo.com"
    assert result[0]["count"] == 3


def test_sorted_by_count_descending():
    emails = [
        make_email("1", "a@many.com"),
        make_email("2", "b@many.com"),
        make_email("3", "c@many.com"),
        make_email("4", "x@few.com"),
    ]
    result = group_by_domain(emails)
    assert result[0]["sender"] == "many.com"
    assert result[1]["sender"] == "few.com"


def test_strips_display_name():
    emails = [make_email("1", "Display Name <user@domain.com>")]
    result = group_by_domain(emails)
    assert result[0]["sender"] == "domain.com"


def test_skips_no_at_sign():
    emails = [
        make_email("1", "not-an-email"),
        make_email("2", "valid@domain.com"),
    ]
    result = group_by_domain(emails)
    assert len(result) == 1
    assert result[0]["sender"] == "domain.com"


def test_email_ids_preserved():
    emails = [
        make_email("abc", "user@test.com", subject="Hello"),
        make_email("def", "other@test.com", subject="World"),
    ]
    result = group_by_domain(emails)
    ids = {e["id"] for e in result[0]["emails"]}
    assert ids == {"abc", "def"}
