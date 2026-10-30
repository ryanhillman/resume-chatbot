# Resume Chatbot

<p align="center">
  <img src="https://img.shields.io/badge/Chatbot-Dialogflow%20ES-FF9800?logo=dialogflow&logoColor=white" />
  <img src="https://img.shields.io/badge/Cloud-Google%20Cloud-4285F4?logo=google-cloud&logoColor=white" />
</p>

This project allows visitors to explore my professional background with a chatbot.

---

## [Demo](https://youtu.be/-dResrRCJoQ)

---

## Screenshot

![Chatbot Screenshot](./docs/screenshot.png)

---

## Features
- Google Dialogflow ES: Handles intents like skills, programming languages, and small talk.
- Webhook (Flask on Cloud Run): Retrieves resume info from a JSON file in Cloud Storage.
- Chatbot embedded using Dialogflow Messenger.
- Links to a PDF version of my resume, LinkedIn, and GitHub.
- Contact Form implemented with [Formspree](https://formspree.io).
- GitHub Pages for static site hosting.
- Frontend designed with HTML5, CSS3, and lightweight JavaScript.

---

## How to Run

### Resumes

Upload `docs/resume.json` and `docs/resume.pdf` to a public Cloud Storage bucket, then update `RESUME_URL` in `backend/main.py` and the Resume link in `index.html`.

### Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Deploy to Cloud Run from the repo root (Dialogflow needs a public URL):

```bash
gcloud run deploy resume-webhook --source backend --allow-unauthenticated
```

### Dialogflow

1. Create a Dialogflow ES agent, zip the contents of `chatbot/`, and import it via **Settings → Export and Import → Restore From Zip**.
2. Under **Fulfillment**, enable the webhook and set the URL to `https://<your-cloud-run-url>/webhook`.

### Frontend

Enable **Integrations → Dialogflow Messenger** and paste your `agent-id` into `index.html`.

Replace the Formspree form ID in `index.html` with your own from [Formspree](https://formspree.io).

Open locally or host with GitHub Pages.

### Tests

```bash
cd backend
pip install -r requirements-dev.txt
pytest
```

---

## Webhook API

The backend exposes one endpoint, called by Dialogflow ES fulfillment.

### `POST /webhook`

**Request:** a standard [Dialogflow ES webhook request](https://cloud.google.com/dialogflow/es/docs/fulfillment-webhook#webhook_request). Only `queryResult.intent.displayName` is used.

```json
{
  "queryResult": {
    "intent": { "displayName": "Languages" }
  }
}
```

**Response:** always `200 OK` with a single text reply.

```json
{
  "fulfillmentText": "Ryan is skilled in\n\n- Java\n- Python\n- JavaScript\n- SQL\n- R"
}
```

**Supported intents**

| Category | Intents |
|---|---|
| Experience | `Experience`, `Accenture`, `NYCERS`, `Bank of America`, `Freshpire`, `CliftonLarsonAllen`, `CPI Security` |
| Skills | `Skills`, `Languages`, `Frameworks`, `Platforms`, `Databases`, `DevOps` |
| Other | `Education`, `Certifications`, `Awards` |

Any other intent name, or a missing/malformed body, returns a general help message.

**Data source:** resume data is read from `resume.json` in Cloud Storage (see `docs/resume.json` for the expected format) and cached for 5 minutes. If the file can't be fetched, the last cached copy is used. With no cached copy, intents reply that no data was found.

### Try it locally

```bash
curl -X POST http://localhost:8080/webhook \
  -H "Content-Type: application/json" \
  -d '{"queryResult": {"intent": {"displayName": "Languages"}}}'
```

---

See the [demo](https://youtu.be/-dResrRCJoQ) for a full walkthrough.
