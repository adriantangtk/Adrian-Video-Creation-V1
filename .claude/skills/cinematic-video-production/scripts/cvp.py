#!/usr/bin/env python3
"""cvp: script-first toolkit for the cinematic-video-production skill.

Deterministic work (scanning, change detection, downloads, frame indexes, transcripts, beat maps, rendering, QC,
the HTML artifact) runs here and is cached on disk. The model reads compact digests and makes the creative calls.
Run `cvp.py <command> -h` for options. Data lives in $CVP_HOME (default: <git root>/clients or ~/cinematic-projects).
"""
import argparse, json, os, shutil, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cvplib import common, store, media, beats, creative, render, qc, artifact  # noqa: E402


def cmd_doctor(a):
    rep, ok = {}, True

    def chk(name, good, detail=""):
        nonlocal ok
        rep[name] = {"ok": bool(good), "detail": detail}
        ok &= bool(good) or name.startswith("optional")
        print(f"{'OK ' if good else 'NO '} {name:28s} {detail}")

    chk("python>=3.9", sys.version_info >= (3, 9), sys.version.split()[0])
    for mod in ("numpy", "PIL"):
        try:
            __import__(mod); chk(mod, True)
        except ImportError:
            chk(mod, False, f"pip install {'pillow' if mod == 'PIL' else mod}")
    for t in ("ffmpeg", "ffprobe", "curl"):
        p = shutil.which(t)
        out = subprocess.run([t, "--version" if t == "curl" else "-version"], capture_output=True, text=True).stdout if p else ""
        ver = (out.splitlines() or ["not found"])[0][:60]
        chk(t, p, ver)
    if shutil.which("ffmpeg"):
        miss = [f for f in ("xfade", "zoompan", "ass", "sidechaincompress", "loudnorm", "signalstats", "blackdetect", "ebur128")
                if subprocess.run(["ffmpeg", "-hide_banner", "-h", f"filter={f}"], capture_output=True).returncode != 0]
        chk("ffmpeg filters", not miss, "missing: " + ", ".join(miss) if miss else "all present")
    fonts = subprocess.run(["fc-list", ":", "family"], capture_output=True, text=True).stdout if shutil.which("fc-list") else ""
    chk("optional: Inter font", "Inter" in fonts, "captions fall back to another sans font if missing")
    chk("optional: npx (whisper)", shutil.which("npx"), "transcription via `npx hyperframes transcribe`")
    models = list(Path.home().glob(".cache/hyperframes/whisper/models/*.bin"))
    chk("optional: whisper model", models, ", ".join(m.name for m in models) or "downloads on first transcription (needs huggingface.co)")
    for host in ("drive.usercontent.google.com", "huggingface.co"):
        r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "-m", "8", f"https://{host}/"], capture_output=True, text=True)
        chk(f"optional: net {host}", r.stdout not in ("", "000") and r.stdout != "403", f"http {r.stdout or 'no answer'}")
    print("AGENT  Google Drive connector     check with the Drive tools (search_files): lists folders, revisions, sizes")
    print("AGENT  Chatcut                    check the tool list for a Chatcut connector; otherwise the FFmpeg editor is used")
    print(f"home   {common.home()}")
    common.wj(common.home() / ".doctor.json", {"time": common.now(), "checks": rep})
    sys.exit(0 if ok else 1)


def cmd_dig(a):
    """Incremental refresh. Step 1 without --listing prints what to list; step 2 with --listing does the rest."""
    pr = common.active_project(a.project)
    src = pr.meta().get("source") or common.die("project has no source folder (set it with `source`)")
    if src["type"] == "drive" and not a.listing:
        lp = pr.p("logs", "drive-listing.tsv")
        print(f"DIG {pr.ref}: list the Drive folder with the Drive connector, all pages, then save it as TSV:")
        print(f"  query: '{src['folder_id']}' in ancestors and trashed = false   (excludeContentSnippets=true, pageSize=100)")
        print(f"  file:  {lp}")
        print("  one line per item: id<TAB>title<TAB>fileSize<TAB>modifiedTime<TAB>mimeType<TAB>parentId")
        print(f"  then:  cvp.py dig --listing {lp} --complete     (--complete only if every page was listed without errors)")
        return
    print(f"== scan ({src['type']})")
    if src["type"] == "drive":
        store.cmd_drive_sync(argparse.Namespace(project=a.project, listing=a.listing, complete=a.complete))
    else:
        store.cmd_local_scan(argparse.Namespace(project=a.project, path=None))
    print("== fetch")
    store.cmd_fetch(argparse.Namespace(project=a.project, ids=None, jobs=3))
    print("== index")
    media.cmd_index(argparse.Namespace(project=a.project, ids=None, jobs=a.jobs, force=False))
    if not a.no_transcribe:
        print("== transcribe")
        media.cmd_transcribe(argparse.Namespace(project=a.project, ids=None, model=None, language=a.language, force=False))
    man = pr.manifest()
    last = man["scans"][-1]
    new_ids = [e["id"] for e in man["media"].values() if e.get("status") == "indexed" and e.get("stages", {}).get("annotated") != e.get("sha256")]
    log = {"time": common.now(), "scan": last, "needs_review": new_ids}
    common.wj(pr.p("logs", f"dig-{common.now()[:19].replace(':', '')}.json"), log)
    print("== result")
    print(json.dumps(last["summary"]))
    if new_ids:
        print(f"new or changed media to review ({len(new_ids)}): {' '.join(new_ids)}")
        print("next: digest --new, look at contact sheets, annotate, re-score hooks, compare against the current storyboards")
    else:
        print("no new or changed media: keep the current edit")


def cmd_source(a):
    pr = common.active_project(a.project)
    m = pr.meta()
    m["source"] = {"type": "drive", "folder_id": a.drive} if a.drive else {"type": "local", "path": str(Path(a.local).resolve())}
    pr.save_meta(m)
    print(f"source set: {m['source']}")


def main():
    ap = argparse.ArgumentParser(prog="cvp.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name, fn, help_):
        p = sub.add_parser(name, help=help_)
        p.add_argument("--project", "-p", help="<client>/<project> (default: active project)")
        p.set_defaults(fn=fn)
        return p

    add("doctor", cmd_doctor, "check tools, filters, network")
    p = add("new", store.cmd_new, "create a client project record and make it active")
    p.add_argument("client"); p.add_argument("project"); p.add_argument("--title")
    p.add_argument("--drive", help="Drive folder id"); p.add_argument("--local", help="local source folder")
    p = add("use", store.cmd_use, "switch active project"); p.add_argument("ref")
    add("list", store.cmd_list, "list all client projects")
    add("status", store.cmd_status, "compact project status")
    p = add("source", cmd_source, "set the project's source folder")
    g = p.add_mutually_exclusive_group(required=True); g.add_argument("--drive"); g.add_argument("--local")
    p = add("drive-sync", store.cmd_drive_sync, "diff a Drive listing against the manifest")
    p.add_argument("listing"); p.add_argument("--complete", action="store_true", help="listing covers every page: allow 'removed'")
    p = add("local-scan", store.cmd_local_scan, "scan a local source folder"); p.add_argument("--path")
    p = add("fetch", store.cmd_fetch, "download pending Drive media into the cache")
    p.add_argument("--ids", nargs="*"); p.add_argument("--jobs", type=int, default=3)
    p = add("add-file", store.cmd_add_file, "register an uploaded file"); p.add_argument("file")
    p = add("index", media.cmd_index, "probe, frame index, scenes, thumbnails, contact sheet, audio stats")
    p.add_argument("--ids", nargs="*"); p.add_argument("--jobs", type=int, default=min(4, os.cpu_count() or 2)); p.add_argument("--force", action="store_true")
    p = add("transcribe", media.cmd_transcribe, "word-level transcripts (cached by checksum)")
    p.add_argument("--ids", nargs="*"); p.add_argument("--model"); p.add_argument("--language"); p.add_argument("--force", action="store_true")
    p = add("digest", media.cmd_digest, "compact table of media, or one item's details")
    p.add_argument("id", nargs="?"); p.add_argument("--new", action="store_true", help="only items not yet annotated")
    p.add_argument("--all", action="store_true"); p.add_argument("--since", type=float)
    p = add("find", media.cmd_find, "search transcripts for words"); p.add_argument("text")
    p = add("frame", media.cmd_frame, "extract stills at times"); p.add_argument("id"); p.add_argument("times", type=float, nargs="+")
    p.add_argument("--full", action="store_true")
    p = add("sheet", media.cmd_sheet, "contact sheet for a time range"); p.add_argument("id")
    p.add_argument("start", type=float); p.add_argument("end", type=float); p.add_argument("--step", type=float, default=0.5)
    p = add("annotate", creative.cmd_annotate, "merge semantic annotations JSON"); p.add_argument("file")
    p = add("hooks", creative.cmd_hooks, "score/rank hooks JSON"); p.add_argument("file"); p.add_argument("--merge", action="store_true")
    p = add("storyboard", creative.cmd_storyboard, "validate + beat-snap a storyboard JSON"); p.add_argument("file")
    p.add_argument("--format", choices=list(common.FORMATS)); p.add_argument("--snap", choices=["none", "beat", "bar"], default="beat")
    p.add_argument("--tolerance", type=float, default=0.12)
    p = add("music-add", beats.cmd_music_add, "add a music track + beat map"); p.add_argument("file")
    for f in ("--id", "--title", "--artist", "--source", "--license"):
        p.add_argument(f)
    p.add_argument("--verified", action="store_true", help="licence checked for commercial/social use")
    p = add("beats", beats.cmd_beats, "show a track's beat map"); p.add_argument("track"); p.add_argument("--force", action="store_true")
    p = add("version-new", render.cmd_version_new, "open the next version folder"); p.add_argument("--note")
    p = add("render", render.cmd_render, "render a storyboard with FFmpeg"); p.add_argument("format", choices=list(common.FORMATS))
    p.add_argument("--draft", action="store_true")
    p = add("qc", qc.cmd_qc, "QC renders of a version"); p.add_argument("--version"); p.add_argument("--file"); p.add_argument("--format")
    add("artifact", artifact.cmd_artifact, "rebuild the HTML artifact")
    p = add("dig", cmd_dig, "incremental refresh of the active project's source")
    p.add_argument("--listing"); p.add_argument("--complete", action="store_true"); p.add_argument("--language")
    p.add_argument("--jobs", type=int, default=min(4, os.cpu_count() or 2)); p.add_argument("--no-transcribe", action="store_true")
    a = ap.parse_args()
    try:
        a.fn(a)
    except RuntimeError as ex:
        common.die(str(ex))


if __name__ == "__main__":
    main()
