#!/usr/bin/env python3
"""Optional per-skill recommended YouTube video.

  python3 tools/skilltree-content/video_gate.py
  python3 tools/skilltree-content/video_gate.py --sample '{"url":"https://youtu.be/dQw4w9WgXcQ"}'

A skill may omit `video`. When the key is present the value is
`{"url", "title"?, "start"?}`.

`url` must be http(s) `youtube.com/watch?v=<id>` or `youtu.be/<id>`
(optional `www.`) with one 11-character id. `start`, when present, is a
non-negative integer. `title`, when present, is a non-empty string.
"""
import json
import os
import re
import sys
from urllib.parse import parse_qs, urlparse

ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DRAFT = os.path.join(ROOT, "skilltree", "ee105_skills_draft.json")
FIELDS = ("url", "title", "start")


def video_error(video):
    """Return an error string, or None when this video value is acceptable.

    Callers skip a missing key. A present null, string, or other non-object
    is an error.
    """
    if not isinstance(video, dict):
        return "video must be an object with a url"
    extra = [k for k in video if k not in FIELDS]
    if extra:
        return "video has unknown fields: " + ", ".join(sorted(extra))
    url = video.get("url")
    if not isinstance(url, str) or not url or any(ch.isspace() for ch in url):
        return "video.url must be a youtube.com/watch or youtu.be link"
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return "video.url must be http or https"
    if parsed.username or parsed.password:
        return "video.url must not include credentials"
    if parsed.port not in (None, 80, 443):
        return "video.url has an unexpected port"
    host = (parsed.hostname or "").lower().rstrip(".")
    if host in ("youtube.com", "www.youtube.com"):
        path = parsed.path.rstrip("/") or "/"
        if path != "/watch":
            return "video.url must be a youtube.com/watch link"
        values = parse_qs(parsed.query, keep_blank_values=True).get("v") or []
        if len(values) != 1:
            return "video.url needs one v= id"
        vid = values[0]
    elif host in ("youtu.be", "www.youtu.be"):
        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) != 1:
            return "video.url must be a youtu.be/<id> link"
        vid = parts[0]
    else:
        return "video.url must be a youtube.com/watch or youtu.be link"
    if not ID_RE.fullmatch(vid):
        return "video id must be 11 characters"
    if "start" in video:
        start = video["start"]
        if isinstance(start, bool) or not isinstance(start, int) or start < 0:
            return "video.start must be a non-negative integer"
    if "title" in video:
        title = video["title"]
        if not isinstance(title, str) or not title.strip():
            return "video.title must be a non-empty string"
    return None


def check_skills(skills):
    errors = []
    with_video = 0
    for skill in skills:
        if "video" not in skill:
            continue
        with_video += 1
        err = video_error(skill.get("video"))
        if err:
            errors.append(f"{skill.get('id', '?')}: {err}")
    return with_video, errors


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "--sample":
        if len(argv) != 2:
            print("usage: video_gate.py --sample <json>", file=sys.stderr)
            return 2
        try:
            video = json.loads(argv[1])
        except json.JSONDecodeError as exc:
            print(f"reject: {exc}")
            return 1
        err = video_error(video)
        if err:
            print(f"reject: {err}")
            return 1
        print("accept")
        return 0
    path = argv[0] if argv else DRAFT
    if len(argv) > 1:
        print("usage: video_gate.py [skills.json] | --sample <json>", file=sys.stderr)
        return 2
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    skills = data["skills"] if isinstance(data, dict) else data
    with_video, errors = check_skills(skills)
    if errors:
        for err in errors:
            print("ERROR", err)
        print(f"video: {len(errors)} error(s)")
        return 1
    print(f"video ok: {len(skills)} skills, {with_video} with a video")
    return 0


if __name__ == "__main__":
    sys.exit(main())
