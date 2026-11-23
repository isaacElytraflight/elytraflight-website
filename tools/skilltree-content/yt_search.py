#!/usr/bin/env python3
"""Search YouTube and print videoRenderer hits. No API key.

  python3 tools/skilltree-content/yt_search.py "<query>"
  python3 tools/skilltree-content/yt_search.py "<query>" --n 8

Fetches https://www.youtube.com/results?search_query=... with a browser
User-Agent, reads ytInitialData, and prints one line per video:

  id | title | channel | duration
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)
ASSIGN = re.compile(r"ytInitialData\s*=\s*")


def fetch_results(query):
    """Return the search-results HTML for this query."""
    url = "https://www.youtube.com/results?" + urllib.parse.urlencode(
        {"search_query": query}
    )
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read()
            charset = resp.headers.get_content_charset() or "utf-8"
    except urllib.error.HTTPError as exc:
        raise SystemExit(f"YouTube returned HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"YouTube request failed: {exc.reason}") from exc
    except TimeoutError as exc:
        raise SystemExit(f"YouTube request failed: {exc}") from exc
    try:
        return raw.decode(charset, "replace")
    except LookupError:
        return raw.decode("utf-8", "replace")


def extract_object(html, start):
    """Return the JSON object that begins at this index, or None."""
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(html)):
        ch = html[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return html[start:i + 1]
    return None


def read_js_string(text, start):
    """Decode one quoted JavaScript string. Return (value, index after it)."""
    quote = text[start]
    if quote not in "\"'":
        raise ValueError("expected a quoted string")
    out = []
    i = start + 1
    while i < len(text):
        ch = text[i]
        if ch == "\\":
            if i + 1 >= len(text):
                break
            nxt = text[i + 1]
            if nxt == "u" and i + 5 < len(text):
                out.append(chr(int(text[i + 2:i + 6], 16)))
                i += 6
                continue
            out.append({
                "n": "\n",
                "r": "\r",
                "t": "\t",
                "b": "\b",
                "f": "\f",
                "\\": "\\",
                "/": "/",
                "'": "'",
                '"': '"',
            }.get(nxt, nxt))
            i += 2
            continue
        if ch == quote:
            return "".join(out), i + 1
        out.append(ch)
        i += 1
    raise ValueError("unterminated string")


def parse_initial_data(html):
    """Return the ytInitialData object."""
    match = ASSIGN.search(html)
    if not match:
        raise SystemExit("ytInitialData not found")
    tail = html[match.end():]
    rest = tail.lstrip()
    origin = match.end() + (len(tail) - len(rest))
    if rest.startswith("{"):
        blob = extract_object(html, origin)
        if blob is None:
            raise SystemExit("ytInitialData object did not end")
        try:
            data = json.loads(blob)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"ytInitialData is not JSON: {exc}") from exc
    elif rest.startswith("JSON.parse("):
        open_paren = origin + len("JSON.parse(")
        while open_paren < len(html) and html[open_paren].isspace():
            open_paren += 1
        try:
            encoded, _end = read_js_string(html, open_paren)
            data = json.loads(encoded)
        except (ValueError, json.JSONDecodeError) as exc:
            raise SystemExit(f"ytInitialData JSON.parse payload failed: {exc}") from exc
    else:
        raise SystemExit("ytInitialData was not a JSON object")
    if not isinstance(data, dict):
        raise SystemExit("ytInitialData was not an object")
    return data


def text_of(node):
    """Join a YouTube text node (simpleText or runs)."""
    if not isinstance(node, dict):
        return ""
    simple = node.get("simpleText")
    if isinstance(simple, str) and simple.strip():
        return simple.strip()
    runs = node.get("runs")
    if isinstance(runs, list):
        parts = []
        for run in runs:
            if isinstance(run, dict) and isinstance(run.get("text"), str):
                parts.append(run["text"])
        return "".join(parts).strip()
    return ""


def one_line(value):
    return " ".join(value.replace("\n", " ").split())


def video_rows(data):
    """Yield (id, title, channel, duration) in page order."""
    seen = set()

    def walk(node):
        if isinstance(node, dict):
            renderer = node.get("videoRenderer")
            if isinstance(renderer, dict):
                vid = renderer.get("videoId")
                if isinstance(vid, str) and vid not in seen and re.fullmatch(r"[A-Za-z0-9_-]{11}", vid):
                    seen.add(vid)
                    title = text_of(renderer.get("title"))
                    channel = (
                        text_of(renderer.get("ownerText"))
                        or text_of(renderer.get("longBylineText"))
                        or text_of(renderer.get("shortBylineText"))
                    )
                    duration = text_of(renderer.get("lengthText"))
                    yield vid, title, channel, duration
            for key, value in node.items():
                if key == "videoRenderer":
                    continue
                yield from walk(value)
        elif isinstance(node, list):
            for item in node:
                yield from walk(item)

    yield from walk(data)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Search YouTube. No API key.")
    parser.add_argument("query", help="search words")
    parser.add_argument("--n", type=int, default=8, help="how many rows to print (default 8)")
    args = parser.parse_args(argv)
    query = (args.query or "").strip()
    if not query:
        print("usage: yt_search.py \"<query>\" [--n 8]", file=sys.stderr)
        return 2
    if args.n < 0:
        print("--n must be >= 0", file=sys.stderr)
        return 2
    html = fetch_results(query)
    data = parse_initial_data(html)
    rows = []
    for row in video_rows(data):
        rows.append(row)
        if len(rows) >= args.n:
            break
    if not rows:
        print("no videoRenderer entries", file=sys.stderr)
        return 1
    for vid, title, channel, duration in rows:
        print(" | ".join(one_line(part) for part in (vid, title, channel, duration)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
