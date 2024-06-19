from enums import IssueStatus


def change_to_valid_email(data: dict):
    email = data.get("author").get("emailAddress") if data.get("author").get("emailAddress") else None
    if email and email.endswith("@enigma.global"):
        email = email.replace("@enigma.global", "@atomgroup.io")
        return email
    return email


def get_valid_status(status: str) -> str:
    if status and status.upper().replace(" ", "_") in IssueStatus:
        return status.upper().replace(" ", "_")
    return IssueStatus.IN_PROGRESS
