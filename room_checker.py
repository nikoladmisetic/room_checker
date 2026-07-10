import json
import os
from pathlib import Path

import requests
from bs4 import BeautifulSoup

URL = "https://borger.eresidentportal.com/apply/default.aspx?RMPROPID=2930"

NTFY_TOPIC = os.getenv("NTFY_TOPIC", "room_tracker")

STATE_FILE = Path("state.json")


def send_notification(message):
    requests.post(
        f"https://ntfy.sh/{NTFY_TOPIC}",
        data=message.encode("utf-8"),
        headers={
            "Title": "🏠 One Bedroom Available!",
            "Priority": "5",
            "Tags": "house"
        },
        timeout=20
    )


def load_previous_status():
    if not STATE_FILE.exists():
        return None

    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f).get("available")
    except Exception:
        return None


def save_status(status):
    with open(STATE_FILE, "w") as f:
        json.dump({"available": status}, f)


def check_availability():
    r = requests.get(URL, timeout=30)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    text = soup.get_text(" ", strip=True)

    if "One Bedroom" not in text:
        return False

    section = text.split("One Bedroom", 1)[1][:300]

    return "0 Available" not in section


def main():
    current = check_availability()
    previous = load_previous_status()

    print(f"Previous: {previous}")
    print(f"Current : {current}")

    if current and previous is not True:
        send_notification(
            f"A one-bedroom apartment appears to be available!\n\n{URL}"
        )

    save_status(current)


if __name__ == "__main__":
    main()
