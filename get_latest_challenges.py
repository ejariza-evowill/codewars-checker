import json
import sys
from datetime import datetime, timezone
from urllib import request, error

USER_URL_TEMPLATE = "https://www.codewars.com/api/v1/users/{}"

API_URL_TEMPLATE = (
    "https://www.codewars.com/api/v1/users/{}/code-challenges/completed?page=0"
)


def fetch_latest(username: str):
    """Return the latest Python challenge for a Codewars user."""
    url = API_URL_TEMPLATE.format(username)
    try:
        with request.urlopen(url) as resp:
            data = json.load(resp)
    except error.HTTPError as e:
        print(f"Failed to fetch data for {username}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error for {username}: {e}")
        return None

    if not data.get("data"):
        return None

    for challenge in data["data"]:
        languages = [lang.lower() for lang in challenge.get("completedLanguages", [])]
        if "python" in languages:
            return challenge
    return None


def fetch_display_name(username: str) -> str:
    """Return the display name for a Codewars user."""
    url = USER_URL_TEMPLATE.format(username)
    try:
        with request.urlopen(url) as resp:
            data = json.load(resp)
    except error.HTTPError as e:
        print(f"Failed to fetch user info for {username}: {e}")
        return username
    except Exception as e:
        print(f"Unexpected error for {username}: {e}")
        return username
    return data.get("name") or data.get("username", username)


def parse_date(date_str: str) -> datetime:
    """Parse ISO 8601 dates from the API."""
    return datetime.fromisoformat(date_str.replace("Z", "+00:00")).astimezone(timezone.utc)


def colorize_date(dt: datetime) -> str:
    """Return a colorized date string based on its age."""
    now = datetime.now(timezone.utc)
    delta = now - dt
    if delta.total_seconds() > 48 * 3600:
        color = "\033[31m"  # red
    elif delta.total_seconds() > 24 * 3600:
        color = "\033[33m"  # yellow
    else:
        color = "\033[32m"  # green
    return f"{color}{dt.strftime("%B %d, %Y, %I:%M:%S %p")}\033[0m"


def main(path: str):
    with open(path, "r", encoding="utf-8") as f:
        usernames = [line.strip() for line in f if line.strip()]

    results = []
    for user in usernames:
        display = fetch_display_name(user)
        latest = fetch_latest(user)
        if not latest:
            print(f"{display} ({user}): No completed Python challenges found")
            continue
        name = latest.get("name") or latest.get("slug")
        date_str = latest.get("completedAt")
        if not date_str:
            print(f"{display} ({user}): {name} (missing completion date)")
            continue
        dt = parse_date(date_str)
        results.append({"user": user, "name": name, "date": dt, "display": display})

    results.sort(key=lambda r: r["date"], reverse=True)

    for item in results:
        colored = colorize_date(item["date"])
        user_label = f"{item['display']} ({item['user']})"
        print(f"- {user_label}: {item['name']} - {colored}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 get_latest_challenges.py <user_list.txt>")
        sys.exit(1)
    main(sys.argv[1])

