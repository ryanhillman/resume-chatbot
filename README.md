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

Upload the PDF and JSON resume files to a Google Cloud storage bucket. 

### Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Deploy to Cloud Run to get a public webhook URL.

### Dialogflow

1. Zip the contents of `chatbot/` and import it via **Settings → Export and Import → Restore From Zip**.
2. Under **Fulfillment**, enable the webhook and set the URL to `https://<your-cloud-run-url>/webhook`.

### Frontend

Enable **Integrations → Dialogflow Messenger** and paste your `agent-id` into `index.html`. 

Open locally or host with GitHub Pages.

---

See the [demo](https://youtu.be/-dResrRCJoQ) for a full walkthrough.
