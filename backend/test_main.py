import main


def test_languages_intent_lists_items(monkeypatch):
    monkeypatch.setattr(main, "load_resume", lambda: {"skills": {"languages": ["Python", "Go"]}})
    client = main.app.test_client()
    resp = client.post("/webhook", json={"queryResult": {"intent": {"displayName": "Languages"}}})
    text = resp.get_json()["fulfillmentText"]
    assert "Python" in text
    assert "Go" in text


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
