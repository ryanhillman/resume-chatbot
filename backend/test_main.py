import json
from pathlib import Path

import pytest

import main

RESUME = json.loads((Path(__file__).parent.parent / "docs" / "resume.json").read_text(encoding="utf-8"))
JOBS = {job["company"]: job for job in RESUME["experience"]}
ACCENTURE = JOBS["Accenture"]["details"]


def role_bullet(name):
    return next(bullets for title, bullets in ACCENTURE.items() if name in title)[0]


@pytest.mark.parametrize(
    "intent, expected",
    [
        ("Experience", JOBS["Accenture"]["role"]),
        ("NYCERS", role_bullet("NYCERS")),
        ("Bank of America", role_bullet("Bank of America")),
        ("Freshpire", JOBS["Freshpire Inc"]["details"][0]),
        ("CliftonLarsonAllen", JOBS["CliftonLarsonAllen LLP"]["details"][0]),
        ("CPI Security", JOBS["CPI Security"]["details"][0]),
        ("Languages", RESUME["skills"]["languages"][0]),
        ("Frameworks", RESUME["skills"]["frameworks"][0]),
        ("Platforms", RESUME["skills"]["platforms"][0]),
        ("Databases", RESUME["skills"]["databases"][0]),
        ("DevOps", RESUME["skills"]["devops"][0]),
        ("Education", RESUME["education"]["school"]),
        ("Certifications", RESUME["certifications"][0]),
        ("Awards", RESUME["awards"][0]),
    ],
)
def test_real_resume_data_reaches_reply(monkeypatch, intent, expected):
    monkeypatch.setattr(main, "load_resume", lambda: RESUME)
    client = main.app.test_client()
    resp = client.post("/webhook", json={"queryResult": {"intent": {"displayName": intent}}})
    assert expected in resp.get_json()["fulfillmentText"]


def test_webhook_intents_match_handlers():
    d = Path(__file__).parent.parent / "chatbot" / "intents"
    intents = [json.loads(p.read_text(encoding="utf-8")) for p in d.glob("*.json") if not p.stem.endswith("_usersays_en")]
    assert {i["name"] for i in intents if i.get("webhookUsed")} == set(main.HANDLERS)


def test_failed_fetch_serves_stale_cache(monkeypatch):
    stale = {"skills": {"languages": ["Python"]}}
    monkeypatch.setattr(main, "_cache", {"data": stale, "fetched_at": 0.0})

    def fail(*args, **kwargs):
        raise main.requests.ConnectionError("unreachable")

    monkeypatch.setattr(main.requests, "get", fail)
    assert main.load_resume() is stale


def test_accenture_intent_returns_fixed_text(monkeypatch):
    monkeypatch.setattr(main, "load_resume", lambda: {})
    client = main.app.test_client()
    resp = client.post("/webhook", json={"queryResult": {"intent": {"displayName": "Accenture"}}})
    text = resp.get_json()["fulfillmentText"]
    assert "NYCERS" in text
    assert "Bank of America" in text


def test_unknown_intent_falls_back(monkeypatch):
    monkeypatch.setattr(main, "load_resume", lambda: {})
    client = main.app.test_client()
    resp = client.post("/webhook", json={"queryResult": {"intent": {"displayName": "Nonsense"}}})
    text = resp.get_json()["fulfillmentText"]
    assert "experience" in text.lower()


def test_malformed_body_does_not_crash(monkeypatch):
    monkeypatch.setattr(main, "load_resume", lambda: {})
    client = main.app.test_client()
    resp = client.post("/webhook", data="not json", content_type="text/plain")
    assert resp.status_code == 200
