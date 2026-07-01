from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

RESUME_URL = "https://storage.googleapis.com/ryan-resume-bucket/resume.json"


def load_resume():
    try:
        r = requests.get(RESUME_URL, timeout=5)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        app.logger.error(f"Failed to fetch resume data: {e}")
        return {}
    except ValueError as e:
        app.logger.error(f"Invalid resume JSON: {e}")
        return {}


def format_experience(job):
    role = job.get("role", "")
    company = job.get("company", "")
    details = job.get("details", [])

    text = f"{role} for {company}"

    if isinstance(details, list) and details:
        text += "\n\n" + "\n".join(f"- {b}" for b in details)

    return text


@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json(silent=True) or {}
    intent = (req.get("queryResult", {}).get("intent", {}) or {}).get("displayName", "")
    data = load_resume()

    # EXPERIENCE
    if intent == "Experience":
        exps = data.get("experience", [])
        if not exps:
            return jsonify({"fulfillmentText": "No experience data found."})
        lines = ["Here is Ryan's professional experience", ""]
        for job in exps:
            role = job.get("role", "")
            company = job.get("company", "")
            if role and company:
                lines.append(f"- {role} at {company}")
        return jsonify({"fulfillmentText": "\n".join(lines)})

    # ACCENTURE overview
    if intent == "Accenture":
        return jsonify({
            "fulfillmentText":
                "Ryan held two roles while at Accenture\n\n"
                "- Cloud Application Developer with NYCERS (New York City Employees Retirement System)\n"
                "- Pegasystems Support with Bank of America (BoA)\n\n"
                "- Would you like to hear more about either?"
        })

    # NYCERS
    if intent in ["NYCERS Details", "Cloud Application Developer Details", "New York City Employee Retirement System Details"]:
        accenture = next((x for x in data.get("experience", []) if x.get("company") == "Accenture"), {})
        bullets = accenture.get("details", {}).get(
            "Cloud Application Developer - New York City Employees Retirement System (NYCERS)", []
        )
        if not bullets:
            return jsonify({"fulfillmentText": "No NYCERS details found."})
        text = "Cloud Application Developer for NYCERS\n\n" + "\n".join(f"- {b}" for b in bullets)
        return jsonify({"fulfillmentText": text})

    # BANK OF AMERICA / PEGASYSTEMS
    if intent in ["BoA Details", "Bank of America Details", "Pegasystems Support Details"]:
        accenture = next((x for x in data.get("experience", []) if x.get("company") == "Accenture"), {})
        bullets = accenture.get("details", {}).get(
            "Pegasystems Support - Bank of America", []
        )
        if not bullets:
            return jsonify({"fulfillmentText": "No Bank of America details found."})
        text = "Pegasystems Support for Bank of America\n\n" + "\n".join(f"- {b}" for b in bullets)
        return jsonify({"fulfillmentText": text})

    # FRESHPIRE
    if intent in ["Freshpire", "Freshpire Details", "Data Migration Details"]:
        job = next((x for x in data.get("experience", []) if x.get("company") == "Freshpire Inc"), {})
        if not job:
            return jsonify({"fulfillmentText": "No Freshpire details found."})
        return jsonify({"fulfillmentText": format_experience(job)})

    # CLIFTON LARSON ALLEN
    if intent in ["CliftonLarsonAllen", "CliftonLarsonAllen Details", "CLA Details", "Tax Accounting Internship"]:
        job = next((x for x in data.get("experience", []) if x.get("company") == "CliftonLarsonAllen LLP"), {})
        if not job:
            return jsonify({"fulfillmentText": "No CliftonLarsonAllen details found."})
        return jsonify({"fulfillmentText": format_experience(job)})

    # CPI SECURITY
    if intent in ["CPI Security", "CPI Security Details", "Inventory Internship"]:
        job = next((x for x in data.get("experience", []) if x.get("company") == "CPI Security"), {})
        if not job:
            return jsonify({"fulfillmentText": "No CPI Security details found."})
        return jsonify({"fulfillmentText": format_experience(job)})

    # SKILLS overview
    if intent == "Skills":
        return jsonify({
            "fulfillmentText":
                "Ryan has experience with Programming Languages, Frameworks/Libraries, Platforms, Databases, and DevOps. "
                "Which would you like to know more about?"
        })

    # SKILLS sub-intents
    if intent == "Languages":
        items = data.get("skills", {}).get("Languages", [])
        if not items:
            return jsonify({"fulfillmentText": "No languages found."})
        return jsonify({"fulfillmentText": "Ryan is skilled in\n\n" + "\n".join(f"- {x}" for x in items)})

    if intent == "Frameworks":
        items = data.get("skills", {}).get("Frameworks & Libraries", [])
        if not items:
            return jsonify({"fulfillmentText": "No frameworks or libraries found."})
        return jsonify({"fulfillmentText": "Ryan has experience with\n\n" + "\n".join(f"- {x}" for x in items)})

    if intent == "Platforms":
        items = data.get("skills", {}).get("Platforms", [])
        if not items:
            return jsonify({"fulfillmentText": "No platforms found."})
        return jsonify({"fulfillmentText": "Ryan has worked with\n\n" + "\n".join(f"- {x}" for x in items)})

    if intent == "Databases":
        items = data.get("skills", {}).get("Databases", [])
        if not items:
            return jsonify({"fulfillmentText": "No databases found."})
        return jsonify({"fulfillmentText": "Ryan is familiar with\n\n" + "\n".join(f"- {x}" for x in items)})

    # DEVOPS
    if intent == "DevOps":
        items = data.get("skills", {}).get("DevOps", [])
        if not items:
            return jsonify({"fulfillmentText": "No DevOps skills found."})
        return jsonify({"fulfillmentText": "Ryan has DevOps experience with\n\n" + "\n".join(f"- {x}" for x in items)})

    # EDUCATION
    if intent == "Education":
        edu = data.get("education", {})
        school = edu.get("school", "")
        degree = edu.get("degree", "")
        grad = edu.get("graduation", "")
        text = f"Ryan earned his degree at {school}. It was a {degree}. He graduated in {grad}."
        return jsonify({"fulfillmentText": text})

    # CERTIFICATIONS
    if intent == "Certifications":
        certs = data.get("certifications", [])
        if not certs:
            return jsonify({"fulfillmentText": "No certifications found."})
        return jsonify({"fulfillmentText": "Ryan holds the following certifications\n\n" + "\n".join(f"- {c}" for c in certs)})

    # AWARDS
    if intent == "Awards":
        awards = data.get("awards", [])
        if isinstance(awards, list):
            return jsonify({
                "fulfillmentText":
                    "Ryan has received the following awards\n\n" + "\n".join(f"- {a}" for a in awards)
                    if awards else "No awards found."
            })

    # FALLBACK
    return jsonify({
        "fulfillmentText":
            "I can help with Ryan's experience, skills, education, certifications, and awards. Please ask about one!"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)