#!/usr/bin/env python3
"""Fetch the transcript of a YouTube video and print it as plain text.

Usage:
    python get_transcript.py <youtube-url-or-id> [--lang ro,en] [--timestamps]

Strategy:
  1. youtube-transcript-api (fast, no API key; manual captions preferred, then auto)
  2. yt-dlp subtitles as fallback
The first line of output is a header: "# <title or id> | lang=<code> | source=<method>".
Exit code 2 = no transcript available, 3 = network/blocked.
"""
import argparse, json, re, subprocess, sys, tempfile, os, glob, html

ID_RE = re.compile(r"(?:v=|/shorts/|/live/|/embed/|youtu\.be/|/v/)([A-Za-z0-9_-]{11})")


def video_id(s: str) -> str:
    s = s.strip()
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", s):
        return s
    m = ID_RE.search(s)
    if not m:
        sys.exit(f"Nu am putut extrage ID-ul video din: {s}")
    return m.group(1)


def fmt(t):
    t = int(t); h, r = divmod(t, 3600); m, s = divmod(r, 60)
    return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:d}:{s:02d}"


def ensure(pkg, mod=None):
    try:
        __import__(mod or pkg)
        return True
    except ImportError:
        r = subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--user", pkg],
                           capture_output=True)
        if r.returncode != 0:
            subprocess.run([sys.executable, "-m", "pip", "install", "-q",
                            "--break-system-packages", pkg], capture_output=True)
        try:
            __import__(mod or pkg); return True
        except ImportError:
            return False


def via_api(vid, langs):
    if not ensure("youtube-transcript-api", "youtube_transcript_api"):
        raise RuntimeError("youtube-transcript-api indisponibil")
    from youtube_transcript_api import YouTubeTranscriptApi
    api = YouTubeTranscriptApi()
    tl = api.list(vid)
    tr = None
    for finder in (tl.find_manually_created_transcript, tl.find_generated_transcript):
        try:
            tr = finder(langs); break
        except Exception:
            pass
    if tr is None:  # any language at all
        tr = next(iter(tl))
    data = tr.fetch()
    segs = [(s.start, s.text) for s in data.snippets]
    return segs, tr.language_code, None


def via_ytdlp(vid, langs):
    if not ensure("yt-dlp", "yt_dlp"):
        raise RuntimeError("yt-dlp indisponibil")
    with tempfile.TemporaryDirectory() as d:
        cmd = [sys.executable, "-m", "yt_dlp", "--skip-download", "--write-subs",
               "--write-auto-subs", "--sub-format", "json3",
               "--sub-langs", ",".join(langs + [l + ".*" for l in langs]),
               "--print-to-file", "%(title)s", os.path.join(d, "title.txt"),
               "-o", os.path.join(d, "%(id)s.%(ext)s"),
               f"https://www.youtube.com/watch?v={vid}"]
        r = subprocess.run(cmd, capture_output=True, text=True)
        files = glob.glob(os.path.join(d, "*.json3"))
        if not files:
            raise RuntimeError(r.stderr.strip()[-500:] or "fără subtitrări")
        f = files[0]
        lang = f.rsplit(".", 2)[-2]
        segs = []
        for ev in json.load(open(f)).get("events", []):
            txt = "".join(x.get("utf8", "") for x in ev.get("segs", []) or []).strip()
            if txt:
                segs.append((ev.get("tStartMs", 0) / 1000, txt))
        title = None
        tp = os.path.join(d, "title.txt")
        if os.path.exists(tp):
            title = open(tp).read().strip()
        return segs, lang, title


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--lang", default="ro,en", help="limbi preferate, separate prin virgulă")
    ap.add_argument("--timestamps", action="store_true",
                    help="prefixează fiecare ~30s de text cu marcaj de timp")
    a = ap.parse_args()
    vid = video_id(a.url)
    langs = [l.strip() for l in a.lang.split(",") if l.strip()]

    errors = []
    for name, fn in (("youtube-transcript-api", via_api), ("yt-dlp", via_ytdlp)):
        try:
            segs, lang, title = fn(vid, langs)
            if segs:
                break
        except Exception as e:
            errors.append(f"{name}: {type(e).__name__}: {str(e)[:300]}")
    else:
        msg = "\n".join(errors)
        print("Nu am putut obține transcrierea.\n" + msg, file=sys.stderr)
        blocked = any(k in msg for k in ("Proxy", "403", "IpBlocked", "RequestBlocked",
                                          "ConnectionError", "Max retries"))
        sys.exit(3 if blocked else 2)

    print(f"# {title or vid} | lang={lang} | source={name} | https://youtu.be/{vid}")
    if a.timestamps:
        block, start = [], None
        for t, txt in segs:
            if start is None:
                start = t
            block.append(txt)
            if t - start >= 30:
                print(f"[{fmt(start)}] " + " ".join(block)); block, start = [], None
        if block:
            print(f"[{fmt(start)}] " + " ".join(block))
    else:
        text = " ".join(html.unescape(t).replace("\n", " ") for _, t in segs)
        print(re.sub(r"\s+", " ", text).strip())


if __name__ == "__main__":
    main()
