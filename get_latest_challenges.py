import json
import sys
from urllib import request, error

API_URL_TEMPLATE = "https://www.codewars.com/api/v1/users/{}/code-challenges/completed?page=0"


def fetch_latest(username: str):
    """Fetch the latest completed challenge for a Codewars user."""
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

    # Data is assumed to be sorted by completion date descending.
    return data["data"][0]


def main(path: str):
    with open(path, "r", encoding="utf-8") as f:
        usernames = [line.strip() for line in f if line.strip()]

    for user in usernames:
        latest = fetch_latest(user)
        if latest:
            name = latest.get("name") or latest.get("slug")
            completed_at = latest.get("completedAt")
            print(f"{user}: {name} ({completed_at})")
        else:
            print(f"{user}: No completed challenges found")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 get_latest_challenges.py <user_list.txt>")
        sys.exit(1)
    main(sys.argv[1])

