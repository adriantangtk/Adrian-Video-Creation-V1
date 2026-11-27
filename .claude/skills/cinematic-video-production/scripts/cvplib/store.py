"""Client/project records, source scanning (Drive listing or local folder), change detection, downloads."""
import csv, hashlib, json, os, shutil, subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from .common import (Project, active_project, set_active, home, rj, wj, now, slug, kind_of, sha256, die)

BRIEF = Path(__file__).resolve().parents[2] / "references" / "project-brief.md"


def mid_for(source_id):
    return "m" + hashlib.sha1(source_id.encode()).hexdigest()[:8]


# ---------------------------------------------------------------- projects

def cmd_new(a):
    c, n = slug(a.client), slug(a.project)
    pr = Project(c, n)
    if pr.p("project.json").exists():
        die(f"{pr.ref} already exists (use `use {pr.ref}`)")
    src = None
    if a.drive:
        src = {"type": "drive", "folder_id": a.drive}
    elif a.local:
        src = {"type": "local", "path": str(Path(a.local).resolve())}
    cl = pr.dir.parents[1] / "client.json"
    if not cl.exists():
        wj(cl, {"client": c, "display_name": a.client, "created": now(), "notes": ""})
    pr.save_meta({"client": c, "project": n, "title": a.title or a.project, "created": now(),
                  "source": src, "formats": ["landscape", "vertical"], "current_version": None})
    pr.save_manifest({"media": {}, "scans": []})
    if BRIEF.exists() and not pr.p("brief.md").exists():
        shutil.copy(BRIEF, pr.p("brief.md"))
    for d in ("index", "music", "storyboards", "versions", "logs"):
        pr.p(d).mkdir(parents=True, exist_ok=True)
    set_active(pr)
    pr.log("new", {"source": src})
    print(f"created {pr.ref} at {pr.dir}\nactive project set. Fill in {pr.p('brief.md')}")


def cmd_use(a):
    pr = active_project(a.ref)
    set_active(pr)
    print(f"active: {pr.ref}")


def cmd_list(a):
    h = home()
    act = rj(h / ".active.json", {})
    for pj in sorted(h.glob("*/projects/*/project.json")):
        m = rj(pj)
        ref = f"{m['client']}/{m['project']}"
        star = "*" if (act.get("client"), act.get("project")) == (m["client"], m["project"]) else " "
        src = (m.get("source") or {}).get("type", "-")
        print(f"{star} {ref:40s} src={src:6s} version={m.get('current_version') or '-'}")


def cmd_status(a):
    pr = active_project(a.project)
    m, man = pr.meta(), pr.manifest()
    media = man["media"]
    from collections import Counter
    kinds = Counter(e["kind"] for e in media.values() if e.get("status") != "removed")
    st = Counter(e.get("status", "?") for e in media.values())
    print(f"project {pr.ref}  ({m.get('title')})\nrecord  {pr.dir}")
    print(f"source  {m.get('source')}")
    print("media   " + ", ".join(f"{k}={v}" for k, v in kinds.items()) or "none")
    print("status  " + ", ".join(f"{k}={v}" for k, v in st.items()))
    sc = man.get("scans", [])
    if sc:
        print(f"last scan {sc[-1]['time']}  {sc[-1].get('summary')}")
    for f in ("hooks.json", "storyboards/landscape.json", "storyboards/vertical.json"):
        print(f"{f:28s} {'yes' if pr.p(f).exists() else 'no'}")
    mus = sorted(p.parent.name for p in pr.p("music").glob("*/track.json"))
    print(f"music   {', '.join(mus) or 'none'}")
    vers = sorted(p.name for p in pr.p("versions").glob("v*"))
    print(f"versions {', '.join(vers) or 'none'}  current={m.get('current_version')}")


# ---------------------------------------------------------------- change detection

def _diff(pr, listed, complete, source_type):
    """listed: {source_id: {name,size,modified,mime,parent,path,md5,local}}"""
    man = pr.manifest()
    media = man["media"]
    by_src = {e["source_id"]: k for k, e in media.items()}
    out = {"new": [], "changed": [], "moved": [], "removed": [], "duplicate": [], "unchanged": 0, "skipped": []}
    for sid, f in listed.items():
        kind = kind_of(f["name"], f.get("mime", ""))
        if kind == "other":
            out["skipped"].append(f["name"])
            continue
        mid = by_src.get(sid) or mid_for(sid)
        e = media.get(mid)
        sig = {"size": f.get("size"), "modified": f.get("modified"), "md5": f.get("md5")}
        if e is None:
            media[mid] = e = {"id": mid, "source_id": sid, "name": f["name"], "kind": kind, "path": f.get("path", f["name"]),
                              "parent": f.get("parent"), "mime": f.get("mime"), **sig, "status": "pending",
                              "first_seen": now(), "history": []}
            if f.get("local"):
                e["local"] = f["local"]
            out["new"].append(mid)
            continue
        if e.get("status") == "removed":
            e["status"] = "pending"
        if any(sig[k] and e.get(k) and str(sig[k]) != str(e.get(k)) for k in sig):
            e["history"].append({k: e.get(k) for k in ("size", "modified", "md5", "sha256")} | {"replaced": now()})
            e.update(sig)
            e["status"] = "pending"
            e.pop("sha256", None)
            e["stages"] = {}
            out["changed"].append(mid)
        elif (f.get("parent"), f["name"]) != (e.get("parent"), e.get("name")):
            e.update(name=f["name"], parent=f.get("parent"), path=f.get("path", f["name"]))
            out["moved"].append(mid)
        else:
            out["unchanged"] += 1
        if f.get("local"):
            e["local"] = f["local"]
    if complete:
        for sid, mid in by_src.items():
            if sid not in listed and media[mid].get("status") != "removed":
                media[mid]["status"] = "removed"
                media[mid]["removed_seen"] = now()
                out["removed"].append(mid)
    # duplicates: same md5/sha, or same size + name
    seen = {}
    for mid, e in media.items():
        if e.get("status") == "removed":
            continue
        key = e.get("sha256") or e.get("md5") or f"{e.get('size')}|{e['name'].lower()}"
        if key in seen and e.get("size"):
            if e.get("duplicate_of") != seen[key]:
                out["duplicate"].append(mid)
            e["duplicate_of"] = seen[key]
        else:
            seen[key] = mid
            e.pop("duplicate_of", None)
    summary = {k: (len(v) if isinstance(v, list) else v) for k, v in out.items()}
    man.setdefault("scans", []).append({"time": now(), "source": source_type, "complete": complete, "summary": summary})
    pr.save_manifest(man)
    pr.log("scan", {"summary": summary, "new": out["new"], "changed": out["changed"], "removed": out["removed"]})
    return out, summary


def _read_listing(path):
    """Accept TSV (id, title, size, modifiedTime, mimeType, parentId[, md5]) or Drive JSON (objects / pages)."""
    txt = Path(path).read_text()
    rows = []
    if txt.lstrip().startswith(("{", "[")):
        data = json.loads(txt)
        pages = data if isinstance(data, list) else [data]
        for pg in pages:
            files = pg.get("files", [pg]) if isinstance(pg, dict) else [pg]
            for f in files:
                rows.append({"id": f["id"], "name": f.get("title") or f.get("name"), "size": f.get("fileSize") or f.get("size"),
                             "modified": f.get("modifiedTime"), "mime": f.get("mimeType", ""), "parent": f.get("parentId"),
                             "md5": f.get("md5Checksum"), "trashed": f.get("trashed", False)})
    else:
        for r in csv.reader([l for l in txt.splitlines() if l.strip() and not l.startswith("#")], delimiter="\t"):
            r += [""] * (7 - len(r))
            rows.append({"id": r[0], "name": r[1], "size": r[2] or None, "modified": r[3] or None, "mime": r[4],
                         "parent": r[5] or None, "md5": r[6] or None, "trashed": False})
    return [r for r in rows if not r["trashed"]]


def cmd_drive_sync(a):
    pr = active_project(a.project)
    src = pr.meta().get("source") or {}
    if src.get("type") != "drive":
        die("project source is not a Drive folder")
    rows = _read_listing(a.listing)
    folders = {r["id"]: r for r in rows if r["mime"] == "application/vnd.google-apps.folder"}
    root = src["folder_id"]

    def path_of(r):
        parts, p, guard = [r["name"]], r.get("parent"), 0
        while p and p != root and p in folders and guard < 30:
            parts.insert(0, folders[p]["name"]); p = folders[p].get("parent"); guard += 1
        return "/".join(parts)

    listed = {r["id"]: {**r, "path": path_of(r)} for r in rows if r["id"] not in folders}
    out, summary = _diff(pr, listed, a.complete, "drive")
    print(json.dumps(summary))
    if not a.complete:
        print("note: listing not marked --complete, so nothing was flagged as removed")


def cmd_local_scan(a):
    pr = active_project(a.project)
    src = pr.meta().get("source") or {}
    root = Path(a.path or src.get("path") or die("no local path"))
    if not root.is_dir():
        die(f"source folder not reachable: {root} (nothing marked removed)")
    listed = {}
    for f in sorted(root.rglob("*")):
        if not f.is_file() or f.name.startswith("."):
            continue
        st = f.stat()
        rel = str(f.relative_to(root))
        mod = str(int(st.st_mtime))
        listed[rel] = {"name": f.name, "size": str(st.st_size), "modified": mod, "parent": str(Path(rel).parent),
                       "path": rel, "local": str(f)}
    out, summary = _diff(pr, listed, True, "local")
    print(json.dumps(summary))


# ---------------------------------------------------------------- downloads

def _download(pr, e):
    ext = Path(e["name"]).suffix.lower() or ".bin"
    dest = pr.media_dir / f"{e['id']}{ext}"
    part = dest.with_name(dest.name + ".part")
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():  # a changed file: keep the previous revision, never overwrite footage
        os.replace(dest, dest.with_name(f"{e['id']}.prev-{now()[:19].replace(':', '')}{ext}"))
    url = f"https://drive.usercontent.google.com/download?id={e['source_id']}&export=download&confirm=t"
    r = subprocess.run(["curl", "-sSL", "--retry", "4", "--retry-delay", "3", "-C", "-", "-o", str(part), url],
                       capture_output=True, text=True)
    if r.returncode not in (0, 33):
        return e["id"], f"curl failed: {r.stderr.strip()[-200:]}"
    with open(part, "rb") as f:
        head = f.read(512).lower()
    if b"<html" in head or b"<!doctype" in head:
        part.unlink()
        return e["id"], "Drive returned a web page: share the file/folder as 'Anyone with the link' (or download it into the source folder)"
    if e.get("size") and part.stat().st_size != int(e["size"]):
        return e["id"], f"size mismatch {part.stat().st_size} != {e['size']} (partial kept, run fetch again)"
    os.replace(part, dest)
    return e["id"], dest


def cmd_fetch(a):
    pr = active_project(a.project)
    man = pr.manifest()
    todo = [e for e in man["media"].values()
            if e.get("status") == "pending" and not e.get("duplicate_of") and (a.ids is None or e["id"] in a.ids)]
    if pr.meta().get("source", {}).get("type") == "local":
        for e in todo:
            e["sha256"] = e.get("sha256") or sha256(e["local"])
            e["status"] = "ready"
        pr.save_manifest(man)
        print(f"local source: {len(todo)} files checksummed in place (originals untouched)")
        return
    ok, bad = 0, []
    with ThreadPoolExecutor(max_workers=a.jobs) as ex:
        for mid, res in ex.map(lambda e: _download(pr, e), todo):
            e = man["media"][mid]
            if isinstance(res, Path):
                e["local"] = str(res.relative_to(pr.dir))
                e["sha256"] = sha256(res)
                e["status"] = "ready"
                e["downloaded"] = now()
                ok += 1
            else:
                e["last_error"] = res
                bad.append((e["name"], res))
    pr.save_manifest(man)
    pr.log("fetch", {"ok": ok, "failed": [b[0] for b in bad]})
    print(f"downloaded {ok}/{len(todo)}")
    for n, err in bad:
        print(f"  FAILED {n}: {err}")


def cmd_add_file(a):
    """Register a file that is already on disk (e.g. an upload) into the manifest and cache."""
    pr = active_project(a.project)
    f = Path(a.file).resolve()
    if not f.is_file():
        die(f"no file {f}")
    dest = pr.media_dir / (mid_for("file:" + f.name) + f.suffix.lower())
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(f, dest)  # copy: never modify originals
    st = dest.stat()
    listed = {"file:" + f.name: {"name": f.name, "size": str(st.st_size), "modified": str(int(f.stat().st_mtime)),
                                 "parent": "uploads", "path": "uploads/" + f.name, "local": str(dest.relative_to(pr.dir))}}
    out, s = _diff(pr, listed, False, "upload")
    man = pr.manifest()
    e = man["media"][mid_for("file:" + f.name)]
    e["sha256"], e["status"] = sha256(dest), "ready"
    pr.save_manifest(man)
    print(f"{e['id']} {f.name} registered")
