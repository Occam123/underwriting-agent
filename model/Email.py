from typing import List, Optional
from datetime import datetime
from model.TextRepFile import TextRepFile

AttachmentType = TextRepFile


class Email:
    def __init__(
        self,
        id: str,
        sender_name: str,
        sender_email: str,
        receiver_names: List[str],
        receiver_emails: List[str],
        datetime: datetime,
        cc: Optional[List[str]] = None,
        subject: str = "",
        body: str = "",
        attachments: Optional[List[AttachmentType]] = None,
        previous_email_id: Optional[str] = None,
        cleaned_body: str = ""
    ):
        self.id = id
        self.sender_name = sender_name
        self.sender_email = sender_email
        self.receiver_names = receiver_names
        self.receiver_emails = receiver_emails
        self.cc = cc or []
        self.subject = subject
        self.body = body
        self.datetime = datetime
        self.attachments = attachments or []
        self.previous_email_id = previous_email_id
        self.cleaned_body = ""

    def __repr__(self):
        return (
            f"Email(id={self.id}, "
            f"from_={self.sender_email}, "
            f"to={self.receiver_emails}, "
            f"subject={self.subject}, "
            f"datetime={self.datetime})"
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "sender_name": self.sender_name,
            "sender_email": self.sender_email,
            "receiver_names": self.receiver_names,
            "receiver_emails": self.receiver_emails,
            "datetime": self.datetime,
            "cc": self.cc,
            "subject": self.subject,
            "body": self.body,
            "attachments": self.attachments,
            "previous_email_id": self.previous_email_id
        }

    def dump(self, dump_attachments: bool = True) -> str:
        INDENT = " " * 2

        def indent_lines(text: str, level: int = 1) -> str:
            prefix = INDENT * level
            return "\n".join(f"{prefix}{line}" for line in text.splitlines())

        # Header
        lines = ["################ Email ################"]
        lines.append(f"id: {self.id}")
        lines.append(f"from: {self.sender_name} {self.sender_email if f'<{self.sender_email}>' else ''}")
        lines.append(f"to:")
        for addr in self.receiver_emails:
            lines.append(f"{INDENT}- {addr}")
        lines.append(f"cc:")
        for addr in self.cc:
            lines.append(f"{INDENT}- {addr}")
        lines.append(f"subject: {self.subject}")

        # Body
        lines.append("body: |")
        lines.append(indent_lines(self.body, level=2))
        
        if dump_attachments:
            # Attachments
            if self.attachments:
                lines.append("attachments:")
                for attachment in self.attachments:
                    lines.append(f"{INDENT}- filename: {attachment.filename}")
                    lines.append(f"{INDENT}  content: |")
                    lines.append(indent_lines(attachment.content, level=3))
            else:
                lines.append("attachments: []")

        return "\n".join(lines)
