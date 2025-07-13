from flask import Flask, request, jsonify
from datetime import datetime
import os
import json
import base64
from traceback import print_exc

from config.Envs import envs
from model.Email import Email
from model.DocumentProcessor import DocumentProcessor
from model.EmailInbox import EmailInbox
from agent.agent import run_agent

app = Flask(__name__)
document_processor = DocumentProcessor()
email_inbox = EmailInbox(callback=run_agent)


def read_email():
    """
    Read email from request or cache
    """
    path = os.path.join("./data", "email.json")

    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        # Serialize file attachments as base64 (for binary safety in JSON)
        attachments = []
        form_data = request.form.to_dict()
        files = request.files
        for key in files:
            file = files[key]
            file_content = file.read()
            attachments.append({
                "filename": file.filename,
                "content_type": file.content_type,
                "content_b64": base64.b64encode(file_content).decode("utf-8")
            })
        email_data = {
            **form_data,
            "attachments": attachments
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(email_data, f, indent=2, ensure_ascii=False)
        return email_data
    else:
        with open(path, "r", encoding="utf-8") as f:
            saved_data = json.load(f)
        return saved_data

@app.route("/email/receive", methods=["POST"])
def receive_email():
    try:
        email = read_email()

        sender = email.get('sender')
        recipient = email.get('recipient')
        subject = email.get('subject')
        body_plain = email.get('body-plain') or email.get('body_plain')
        timestamp = email.get('timestamp')
        message_headers = email.get('message-headers')

        message_id = None
        previous_email_id = None  # <--- for threading!

        if message_headers:
            try:
                headers = json.loads(message_headers)
                for header in headers:
                    header_name = header[0].lower()
                    header_value = header[1]
                    if header_name == 'message-id':
                        message_id = header_value
                    elif header_name == 'in-reply-to':
                        previous_email_id = header_value
                # If "In-Reply-To" not present, try "References" for a chain
                if not previous_email_id:
                    for header in headers:
                        if header[0].lower() == 'references':
                            refs = header[1]
                            # Take the last message-id in references as previous, if it's a space-separated string
                            if isinstance(refs, str):
                                parts = refs.strip().split()
                                if parts:
                                    previous_email_id = parts[-1]
                            break
            except Exception as e:
                print_exc()
                print("Error parsing headers:", e)

        # Convert timestamp to datetime
        if timestamp:
            received_at = datetime.fromtimestamp(float(timestamp))
        else:
            received_at = datetime.now()

        # Attachments from email data (already base64 encoded content)
        attachments = email.get("attachments", [])

        text_rep_attachments = []
        try:
            for attachment in attachments:
                content_b64 = attachment["content_b64"]
                filename = attachment.get("filename", "file")
                content = base64.b64decode(content_b64)
                text_rep_of_attachment = document_processor.document_to_text(filename, content)
                text_rep_attachments.append(text_rep_of_attachment)
        except Exception as e:
            print("Failed to process attachment")
            print(e)
            print_exc()


        internal_rep_email = Email(
            id=message_id,
            sender_name=sender,
            sender_email=sender,
            receiver_names=[recipient] if recipient else [],
            receiver_emails=[recipient] if recipient else [],
            datetime=received_at,
            cc=[],
            subject=subject,
            body=body_plain,
            attachments=text_rep_attachments,
            previous_email_id=previous_email_id
        )

        email_inbox.push(internal_rep_email)

        return jsonify({
            "status": "ok",
            "received": True,
            "processed": True,
            "message_id": message_id,
            "previous_email_id": previous_email_id,
            "chained": previous_email_id is not None
        })
    except Exception as e:
        print(f"Error processing email")
        print(e)
        print_exc()
        return jsonify({"status": "error", "message": str(e)}), 200

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
