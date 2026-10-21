#!/usr/bin/env python3
"""Refresh the lucas-smi and csl.log blocks in README.md.

Reads ONLY the hard-allowlisted public repos below via the GitHub REST API
with the workflow's GITHUB_TOKEN. No org-wide listing, no PAT.
"""
import datetime as dt, json, os, re, sys, urllib.request
from zoneinfo import ZoneInfo
sys.path.insert(0, os.path.dirname(__file__))
from lucas_smi import smi, GPUS

ALLOWLIST = ("CSL-Laboratories/recursion", "CSL-Laboratories/ai-investment-cockpit")  # exactly these two
TZ = ZoneInfo("America/Los_Angeles")
TOKEN = os.environ["GITHUB_TOKEN"]
README = os.environ.get("README_PATH", "README.md")
DOC_RE = re.compile(r"(\.md$|\.mdx$|\.rst$|\.txt$|^docs/)")

def api(path):
    req = urllib.request.Request(f"https://api.github.com{path}", headers={
        "Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def ts(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(TZ)

def merged_prs(repo, n=5):
    pulls = api(f"/repos/{repo}/pulls?state=closed&sort=updated&direction=desc&per_page=30")
    out = []
    for p in (p for p in pulls if p.get("merged_at")):
        detail = api(f"/repos/{repo}/pulls/{p['number']}")
        files = api(f"/repos/{repo}/pulls/{p['number']}/files?per_page=100")
        kind = "G" if files and all(DOC_RE.search(f["filename"]) for f in files) else "C"
        out.append(dict(repo=repo.split("/")[1], number=p["number"], title=p["title"],
                        when=ts(p["merged_at"]), kind=kind,
                        mem=f"+{detail['additions']} / -{detail['deletions']}"))
        if len(out) >= n:
            break
    return out

def releases(repo, n=3):
    return [dict(repo=repo.split("/")[1], tag=r["tag_name"], when=ts(r["published_at"]))
            for r in api(f"/repos/{repo}/releases?per_page={n}") if r.get("published_at")]

def replace(text, name, body):
    pat = re.compile(rf"(<!-- {name}:start -->)(.*?)(<!-- {name}:end -->)", re.S)
    if not pat.search(text):
        sys.exit(f"marker {name} missing")
    return pat.sub(lambda m: f"{m.group(1)}\n{body}\n{m.group(3)}", text)

def main():
    prs = sorted((p for r in ALLOWLIST for p in merged_prs(r)), key=lambda p: p["when"], reverse=True)
    rels = [x for r in ALLOWLIST for x in releases(r)]
    procs = [(p["number"], p["kind"], p["repo"], p["mem"]) for p in prs[:5]]
    smi_md = "```text\n" + smi(GPUS, procs) + "\n```"
    events = [(p["when"], f"{p['repo']}: merged #{p['number']} {p['title']}") for p in prs] + \
             [(r["when"], f"{r['repo']}: released {r['tag']}") for r in rels]
    events.sort(reverse=True)
    log = "".join(f"[{w:%Y-%m-%d %H:%M}] {msg}\n" for w, msg in events[:8])
    csl_md = "```console\n$ tail -f /var/log/csl.log\n" + log + "```"
    text = open(README, encoding="utf-8").read()
    new = replace(replace(text, "smi", smi_md), "csl", csl_md)
    if new != text:
        new = replace(new, "updated", f"<sub>Last updated {dt.datetime.now(TZ):%Y-%m-%d %H:%M} PT by github-actions[bot]</sub>")
        open(README, "w", encoding="utf-8").write(new)
        print("README updated")
    else:
        print("no changes")

if __name__ == "__main__":
    main()
