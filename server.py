import json
import os
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from pathlib import Path
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "messages.json"

HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8000"))

MAIL_USERNAME = os.environ.get("balas.karthik@gmail.com")
MAIL_PASSWORD = os.environ.get("kihtrakb321")
MAIL_TO = os.environ.get("MAIL_TO") or MAIL_USERNAME
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
IMAP_SERVER = os.environ.get("IMAP_SERVER", "imap.gmail.com")
IMAP_PORT = int(os.environ.get("IMAP_PORT", "993"))
IMAP_USERNAME = os.environ.get("IMAP_USERNAME") or MAIL_USERNAME
IMAP_PASSWORD = os.environ.get("IMAP_PASSWORD") or MAIL_PASSWORD


def load_messages():
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def save_messages(messages):
    DATA_FILE.write_text(json.dumps(messages, indent=2), encoding="utf-8")


def add_message(messages, role, text, name=None, email=None, source="web"):
    messages.append({
        "id": len(messages) + 1,
        "role": role,
        "text": text,
        "name": name,
        "email": email,
        "source": source,
        "timestamp": __import__("datetime").datetime.utcnow().isoformat() + "Z"
    })
    save_messages(messages)


def send_email_notification(name, email, message):
    if not MAIL_USERNAME or not MAIL_PASSWORD or not MAIL_TO:
        print("Email configuration not complete; skipping outbound mail.")
        return False

    body = f"Portfolio contact received from {name} <{email}>\n\n{message}"
    msg = MIMEText(body)
    msg["Subject"] = f"New portfolio chat from {name}"
    msg["From"] = MAIL_USERNAME
    msg["To"] = MAIL_TO

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(MAIL_USERNAME, MAIL_PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception as exc:
        print(f"Failed to send email: {exc}")
        return False


def get_email_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    return payload.decode(errors="ignore")
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            return payload.decode(errors="ignore")
    return ""


def fetch_replies(messages):
    if not IMAP_USERNAME or not IMAP_PASSWORD:
        return messages

    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(IMAP_USERNAME, IMAP_PASSWORD)
        mail.select("INBOX")
        status, data = mail.search(None, "UNSEEN")
        for item in data[0].split():
            status, msg_data = mail.fetch(item, "(RFC822)")
            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)
            body = get_email_body(msg).strip() or "A reply was received."
            if not any(existing.get("text") == body and existing.get("source") == "email" for existing in messages):
                add_message(messages, "bot", body, source="email")
            mail.store(item, "+FLAGS", "\\Seen")
        mail.logout()
    except Exception as exc:
        print(f"Failed to retrieve email replies: {exc}")
    return messages


class PortfolioHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/messages":
            messages = load_messages()
            messages = fetch_replies(messages)
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"messages": messages}).encode("utf-8"))
            return

        if parsed.path == "/":
            file_path = ROOT / "index.html"
        else:
            file_path = ROOT / parsed.path.lstrip("/")

        if file_path.exists() and file_path.is_file():
            content_type = "text/html" if file_path.suffix.lower() in {".html", ".htm"} else "application/octet-stream"
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type)
            self.end_headers()
            self.wfile.write(file_path.read_bytes())
        else:
            self.send_response(HTTPStatus.NOT_FOUND)
            self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/messages":
            self.send_response(HTTPStatus.NOT_FOUND)
            self.end_headers()
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(content_length).decode("utf-8")
        try:
            payload = json.loads(body or "{}")
        except json.JSONDecodeError:
            payload = {}

        messages = load_messages()
        name = (payload.get("name") or "Visitor").strip()
        email = (payload.get("email") or "unknown").strip()
        message = (payload.get("message") or "").strip()
        if message:
            add_message(messages, "user", message, name=name, email=email, source="web")
            send_email_notification(name, email, message)

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode("utf-8"))


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), PortfolioHandler)
    print(f"Portfolio server listening on http://{HOST}:{PORT}")
    server.serve_forever()
