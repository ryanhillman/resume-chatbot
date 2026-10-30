import os
import time

from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

RESUME_URL = os.environ.get(
    "RESUME_URL", "https://storage.googleapis.com/ryan-resume-bucket/resume.json"
)
CACHE_TTL_SECONDS = 300

FALLBACK_TEXT = (
    "I can help with Ryan's experience, skills, education, certifications, and awards. Please ask about one!"
)

_cache = {"data": None, "fetched_at": 0.0}


def load_resume():
    now = time.time()
    if _cache["data"] is not None and now - _cache["fetched_at"] < CACHE_TTL_SECONDS:
        return _cache["data"]

    try:
        r = requests.get(RESUME_URL, timeout=5)
        r.raise_for_status()
        data = r.json()
    except requests.RequestException as e:
        app.logger.error(f"Failed to fetch resume data: {e}")
        return _cache["data"] or {}
    except ValueError as e:
        app.logger.error(f"Invalid resume JSON: {e}")
        return _cache["data"] or {}

    _cache["data"] = data
    _cache["fetched_at"] = now
    return data


def bullet_list(items):
    return "\n".join(f"- {item}" for item in items)


def find_job(data, company):
    return next((x for x in data.get("experience", []) if x.get("company") == company), {})


def format_experience(job):
    text = f"{job.get('role', '')} for {job.get('company', '')}"
    details = job.get("details", [])
    if isinstance(details, list) and details:
        text += "\n\n" + bullet_list(details)
    return text


def experience(data):
    jobs = data.get("experience", [])
    if not jobs:
        return "No experience data found."
    lines = ["Here is Ryan's professional experience", ""]
    for job in jobs:
        role = job.get("role", "")
        company = job.get("company", "")
        if role and company:
            lines.append(f"- {role} at {company}")
    return "\n".join(lines)


def education(data):
    edu = data.get("education", {})
    return (
        f"Ryan earned his degree at {edu.get('school', '')}. It was a {edu.get('degree', '')}. "
        f"He graduated in {edu.get('graduation', '')}."
    )


def fixed_reply(text):
    return lambda data: text


def accenture_role(details_key, title, label):
    def handler(data):
        bullets = find_job(data, "Accenture").get("details", {}).get(details_key, [])
        if not bullets:
            return f"No {label} details found."
        return f"{title}\n\n{bullet_list(bullets)}"
    return handler


def job_reply(company, label):
    def handler(data):
        job = find_job(data, company)
        if not job:
            return f"No {label} details found."
        return format_experience(job)
    return handler


def list_reply(intro, missing, *path):
    def handler(data):
        items = data
        for key in path:
            items = items.get(key, {})
        if not items:
            return missing
        return f"{intro}\n\n{bullet_list(items)}"
    return handler


HANDLERS = {
    "Experience": experience,
    "Accenture": fixed_reply(
        "Ryan held two roles while at Accenture\n\n"
        "- Cloud Application Developer with NYCERS (New York City Employees Retirement System)\n"
        "- Pegasystems Support with Bank of America (BoA)\n\n"
        "Ask about NYCERS or Bank of America to hear more."
    ),
    "NYCERS": accenture_role(
        "Cloud Application Developer - New York City Employees Retirement System (NYCERS)",
        "Cloud Application Developer for NYCERS",
        "NYCERS",
    ),
    "Bank of America": accenture_role(
        "Pegasystems Support - Bank of America",
        "Pegasystems Support for Bank of America",
        "Bank of America",
    ),
    "Freshpire": job_reply("Freshpire Inc", "Freshpire"),
    "CliftonLarsonAllen": job_reply("CliftonLarsonAllen LLP", "CliftonLarsonAllen"),
    "CPI Security": job_reply("CPI Security", "CPI Security"),
    "Skills": fixed_reply(
        "Ryan has experience with Programming Languages, Frameworks/Libraries, Platforms, Databases, and DevOps. "
        "Which would you like to know more about?"
    ),
    "Languages": list_reply("Ryan is skilled in", "No languages found.", "skills", "languages"),
    "Frameworks": list_reply("Ryan has experience with", "No frameworks or libraries found.", "skills", "frameworks"),
    "Platforms": list_reply("Ryan has worked with", "No platforms found.", "skills", "platforms"),
    "Databases": list_reply("Ryan is familiar with", "No databases found.", "skills", "databases"),
    "DevOps": list_reply("Ryan has DevOps experience with", "No DevOps skills found.", "skills", "devops"),
    "Education": education,
    "Certifications": list_reply(
        "Ryan holds the following certifications", "No certifications found.", "certifications"
    ),
    "Awards": list_reply("Ryan has received the following awards", "No awards found.", "awards"),
}


@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json(silent=True) or {}
    intent = (req.get("queryResult", {}).get("intent", {}) or {}).get("displayName", "")
    handler = HANDLERS.get(intent)
    text = handler(load_resume()) if handler else FALLBACK_TEXT
    return jsonify({"fulfillmentText": text})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
