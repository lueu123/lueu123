#!/usr/bin/env python3
"""Fetch LeetCode stats and patch them into fastfetch.svg."""

import json
import pathlib
import re
import sys
import urllib.request

USERNAME = "lueu123"

ROOT = pathlib.Path(__file__).resolve().parent.parent
SVG_PATH = ROOT / "fastfetch.svg"

QUERY = """
query($u: String!) {
  allQuestionsCount { difficulty count }
  matchedUser(username: $u) {
    submitStatsGlobal {
      acSubmissionNum { difficulty count }
    }
  }
}
"""


def fetch(username):
    payload = json.dumps({"query": QUERY, "variables": {"u": username}}).encode()
    req = urllib.request.Request(
        "https://leetcode.com/graphql",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Referer": "https://leetcode.com",
            "User-Agent": "Mozilla/5.0 (readme-stats)",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        body = json.load(r)

    if body.get("errors"):
        sys.exit(f"LeetCode returned errors: {body['errors']}")

    data = body["data"]
    if not data.get("matchedUser"):
        sys.exit(f"No such user (or profile is private): {username}")

    totals = {x["difficulty"]: x["count"] for x in data["allQuestionsCount"]}
    solved = {
        x["difficulty"]: x["count"]
        for x in data["matchedUser"]["submitStatsGlobal"]["acSubmissionNum"]
    }
    return totals, solved


def build_row(totals, solved):
    return (
        f'<tspan fill="#7ee787">{solved["All"]}</tspan>'
        f'<tspan fill="#8b949e"> \u00b7 </tspan>'
        f'<tspan fill="#7ee787">E {solved["Easy"]}</tspan>'
        f'<tspan fill="#8b949e"> \u00b7 </tspan>'
        f'<tspan fill="#d29922">M {solved["Medium"]}</tspan>'
        f'<tspan fill="#8b949e"> \u00b7 </tspan>'
        f'<tspan fill="#f85149">H {solved["Hard"]}</tspan>'
    )


def main():
    totals, solved = fetch(USERNAME)
    row = build_row(totals, solved)

    svg = SVG_PATH.read_text(encoding="utf-8")
    new_svg, n = re.subn(
        r"(<!--LC_START-->).*?(<!--LC_END-->)",
        lambda m: m.group(1) + row + m.group(2),
        svg,
        flags=re.DOTALL,
    )
    if n != 1:
        sys.exit(f"Expected 1 marker pair in fastfetch.svg, found {n}.")

    if new_svg == svg:
        print("No change.")
        return

    SVG_PATH.write_text(new_svg, encoding="utf-8")
    print(f"Updated: {solved['All']}/{totals['All']} solved")


if __name__ == "__main__":
    main()
