from flask import Flask, render_template, request
# import smtplib
# from email.mime.text import MIMEText
import json
import time

app = Flask(__name__)

with open("resume.json", "r", encoding="utf-8") as f:
    resume = json.load(f)

chat_request_times = {}
email_request_times = {}
MIN_DELAY = 5


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/chat", methods=["POST"])
def chat():
    ip = request.remote_addr
    now = time.time()

    last = chat_request_times.get(ip, 0)
    if now - last < MIN_DELAY:
        return render_template(
            "result.html",
            result=f"Please wait {int(MIN_DELAY - (now - last))} seconds before next question.",
        )
    chat_request_times[ip] = now

    question = request.form.get("question", "").lower()
    answer = "I couldn’t find that in the resume."

    if "name" in question or "who" in question:
        answer = resume["name"]

    elif "email" in question:
        answer = resume["email"]

    elif "phone" in question or "contact" in question:
        answer = resume["phone"]

    elif "address" in question or "live" in question or "location" in question:
        answer = resume["address"]

    elif "title" in question or "role" in question or "position" in question:
        answer = resume["title"]

    elif "summary" in question or "about" in question:
        answer = resume["summary"]

    elif "experience" in question or "work" in question or "job" in question:
        exp_list = [
            f"• {e['role']} at {e['company']} ({e['duration']})\n  - "
            + "\n  - ".join(e["details"])
            for e in resume["experience"]
        ]
        answer = "\n\n".join(exp_list)

    elif "project" in question:
        proj_list = [
            f"• {p['name']}\n  Stack: {', '.join(p['stack'])}\n  Features: {', '.join(p['features'])}"
            for p in resume["projects"]
        ]
        answer = "\n\n".join(proj_list)

    elif "education" in question or "study" in question or "college" in question:
        edu_list = [
            f"• {e['field']} at {e['institution']} ({e['duration']})"
            for e in resume["education"]
        ]
        answer = "\n".join(edu_list)

    elif "skill" in question or "technology" in question:
        answer = ", ".join(resume["skills"])

    elif "language" in question:
        answer = ", ".join(resume["languages"])

    else:
        matches = []

        def search_json(data, section_name=""):
            if isinstance(data, dict):
                for k, v in data.items():
                    if isinstance(v, str) and question in v.lower():
                        matches.append(format_section(section_name, data))
                        break
                    else:
                        search_json(v, section_name or k)
            elif isinstance(data, list):
                for item in data:
                    search_json(item, section_name)

        def format_section(section, obj):
            """Format dictionary into aligned text"""
            if section == "experience":
                return (
                    f"• {obj['role']} at {obj['company']} ({obj['duration']})\n  - "
                    + "\n  - ".join(obj["details"])
                )
            elif section == "projects":
                return f"• {obj['name']}\n  Stack: {', '.join(obj['stack'])}\n  Features: {', '.join(obj['features'])}"
            elif section == "education":
                return f"• {obj['field']} at {obj['institution']} ({obj['duration']})"
            else:
                return "\n".join(
                    [f"{k}: {v}" for k, v in obj.items() if isinstance(v, str)]
                )

        search_json(resume)

        if matches:
            answer = "\n\n".join(matches)

    return render_template("result.html", result=answer)


@app.route("/send-email", methods=["POST"])
def send_email():

    ip = request.remote_addr
    now = time.time()

    last = email_request_times.get(ip, 0)
    if now - last < MIN_DELAY:
        return render_template(
            "result.html",
            result=f"Please wait {int(MIN_DELAY - (now - last))} seconds before sending another email.",
        )
    email_request_times[ip] = now

    recipient = request.form.get("recipient", "")
    subject = request.form.get("subject", "")
    body = request.form.get("body", "")

    # --- Mock sending email ---
    print(f"[Mock Email] To: {recipient} | Subject: {subject}\n{body}")
    result = f"Email simulated! To: {recipient}, Subject: {subject}"

    # --- Real SMTP code (commented out) ---
    """
    SMTP_SERVER = "sandbox.smtp.mailtrap.io"
    SMTP_PORT = 2525
    SMTP_USER = ""
    SMTP_PASS = ""

    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = SMTP_USER
        msg["To"] = recipient

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)

        result = f"Email sent safely! To: {recipient}, Subject: {subject}"

    except Exception as e:
        result = f"Error sending email: {e}"
    """

    return render_template("result.html", result=result)




if __name__ == "__main__":
    app.run(debug=True)
    # app.run(host="0.0.0.0", port=5001, debug=True, threaded=True)