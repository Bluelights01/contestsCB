import requests
import json
import re
from typing import List, Dict, Optional


HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; FetchBot/1.0)",
    "Content-Type": "application/json",
    "Referer": "https://leetcode.com"
}

GRAPHQL_QUERY = """
query recentSubs($username: String!, $limit: Int!) {
  recentSubmissionList(username: $username, limit: $limit) {
    title
    titleSlug
    statusDisplay
    timestamp
  }
}
"""

def fetch_recent_submissions_graphql(username: str, limit: int = 10, timeout: int = 10) -> Optional[List[Dict]]:
    """Try GraphQL endpoint to fetch recentSubmissionList."""
    url = "https://leetcode.com/graphql"
    payload = {"query": GRAPHQL_QUERY, "variables": {"username": username, "limit": limit}}
    try:
        resp = requests.post(url, json=payload, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
        j = resp.json()
        # GraphQL returns data.recentSubmissionList
        submissions = j.get("data", {}).get("recentSubmissionList")
        if submissions:
            return submissions
        return None
    except Exception:
        return None

def extract_json_array_from_text(text: str, key: str) -> Optional[List]:
    """
    Attempt to find "<key>": [ ... ] JSON array in text using regex,
    then load the array with json.loads (fixing single quotes if needed).
    """
    pattern = re.compile(rf'"{re.escape(key)}"\s*:\s*(\[\s*\{{.*?\}}\s*\])', re.DOTALL)
    m = pattern.search(text)
    if not m:
        # fallback: try without surrounding object braces (looser)
        pattern2 = re.compile(rf'{re.escape(key)}"\s*:\s*(\[\s*.+?\])', re.DOTALL)
        m = pattern2.search(text)
        if not m:
            return None
    array_text = m.group(1)
    # sometimes the JSON in-page is escaped or contains unquoted keys; try to fix common issues
    try:
        return json.loads(array_text)
    except Exception:
        # Try to unescape common escapes (this may help)
        try:
            cleaned = array_text.encode('utf-8').decode('unicode_escape')
            return json.loads(cleaned)
        except Exception:
            return None

def fetch_recent_submissions_from_profile_html(username: str, limit: int = 10, timeout: int = 10) -> Optional[List[Dict]]:
    """Fetch user's profile page and try to extract recentSubmissionList JSON from the HTML."""
    url = f"https://leetcode.com/{username}/"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
        text = resp.text

        # Try to find JSON blob "recentSubmissionList": [...]
        submissions = extract_json_array_from_text(text, "recentSubmissionList")
        if submissions:
            return submissions[:limit]

        # Another heuristic: some pages embed JSON in a script tag with window.__INITIAL_STATE__ or __NEXT_DATA__
        # Try to locate a big JSON object inside <script> tags
        script_json_match = re.search(r'__NEXT_DATA__\s*=\s*({.*?});\s*</script>', text, re.DOTALL)
        if not script_json_match:
            script_json_match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});\s*</script>', text, re.DOTALL)
        if script_json_match:
            try:
                big = json.loads(script_json_match.group(1))
                # Try to walk the big object to find recentSubmissionList
                def find_key(obj, key):
                    if isinstance(obj, dict):
                        if key in obj and isinstance(obj[key], list):
                            return obj[key]
                        for v in obj.values():
                            found = find_key(v, key)
                            if found:
                                return found
                    elif isinstance(obj, list):
                        for item in obj:
                            found = find_key(item, key)
                            if found:
                                return found
                    return None
                found = find_key(big, "recentSubmissionList")
                if found:
                    return found[:limit]
            except Exception:
                pass

        return None
    except Exception:
        return None

def fetch_latest_solved(username: str, limit: int = 10, solved_only: bool = True) -> List[Dict]:
    """
    Return recent submissions (dicts) for the username.
    Each dict contains at least: title, titleSlug, statusDisplay, timestamp.
    If solved_only=True, only returns submissions where statusDisplay is 'Accepted'.
    """
    # 1) try GraphQL
    subs = fetch_recent_submissions_graphql(username, limit=limit)
    if not subs:
        # 2) fallback to profile HTML parsing
        subs = fetch_recent_submissions_from_profile_html(username, limit=limit)
    if not subs:
        # final fallback: empty list
        return []

    # Normalize & filter
    normalized = []
    for s in subs:
        entry = {
            "title": s.get("title"),
            "slug": s.get("titleSlug"),
            "status": s.get("statusDisplay"),
            "timestamp": s.get("timestamp"),
        }
        if solved_only:
            if entry["status"] and entry["status"].lower() in ("accepted", "ac"):
                normalized.append(entry)
        else:
            normalized.append(entry)
        if len(normalized) >= limit:
            break
    return normalized
fetch_recent_submissions_graphql("bluelights")

