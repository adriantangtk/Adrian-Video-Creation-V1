"""Shared helpers: paths, JSON I/O, subprocess, project resolution, locking."""
import contextlib, datetime as dt, fcntl, gzip, hashlib, json, os, re, shutil, subprocess, sys
from pathlib import Path

VIDEO_EXT = {".mp4", ".mov", ".m4v", ".mkv", ".avi", ".mts", ".m2ts", ".webm", ".3gp", ".mxf"}
AUDIO_EXT = {".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg", ".opus", ".aif", ".aiff"}
PHOTO_EXT = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp", ".tif", ".tiff", ".bmp", ".dng"}
FORMATS = {"landscape": (1920, 1080), "vertical": (1080, 1920)}
# Text safe zones (x0, y0, x1, y1) in output pixels.
SAFE = {"landscape": (96, 54, 1824, 1026), "vertical": (60, 250, 940, 1440)}


def now():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def die(msg, code=1):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def slug(s):
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s.strip().lower()).strip("-")
    return s or "untitled"


def kind_of(name, mime=""):
    ext = Path(name).suffix.lower()
    if mime.startswith("video/") or ext in VIDEO_EXT:
        return "video"
    if mime.startswith("audio/") or ext in AUDIO_EXT:
        return "audio"
    if mime.startswith("image/") or ext in PHOTO_EXT:
        return "photo"
    return "other"


def rj(path, default=None):
    p = Path(path)
    if not p.exists():
        return default
    with (gzip.open(p, "rt") if p.suffix == ".gz" else open(p)) as f:
        return json.load(f)


def wj(path, data):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + ".tmp")
    with open(tmp, "w") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
    os.replace(tmp, p)


def run(cmd, check=True, capture=True, **kw):
    r = subprocess.run(cmd, capture_output=capture, text=True, **kw)
    if check and r.returncode != 0:
        tail = (r.stderr or "")[-1500:]
        raise RuntimeError(f"command failed ({r.returncode}): {' '.join(map(str, cmd[:6]))} ...\n{tail}")
    return r


def sha256(path, bufsize=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(bufsize):
            h.update(chunk)
    return h.hexdigest()


def short_hash(obj):
    return hashlib.sha1(json.dumps(obj, sort_keys=True).encode()).hexdigest()[:12]


def fmt_t(t):
    t = float(t)
    return f"{int(t // 60)}:{t % 60:05.2f}"


# ---------------------------------------------------------------- locations

def home():
    env = os.environ.get("CVP_HOME")
    if env:
        p = Path(env)
    else:
        r = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
        p = Path(r.stdout.strip()) / "clients" if r.returncode == 0 else Path.home() / "cinematic-projects"
    p.mkdir(parents=True, exist_ok=True)
    gi = p / ".gitignore"
    if not gi.exists():
        gi.write_text("# heavy, re-creatable data stays out of git\n*/projects/*/cache/\n*/projects/*/versions/*/drafts/\n")
    return p


class Project:
    """One client project record: <home>/<client>/projects/<project>/"""

    def __init__(self, client, name):
        self.client, self.name = client, name
        self.dir = home() / client / "projects" / name

    @property
    def ref(self):
        return f"{self.client}/{self.name}"

    def p(self, *parts):
        return self.dir.joinpath(*parts)

    # layout
    @property
    def cache(self): return self.p("cache")
    @property
    def media_dir(self): return self.p("cache", "media")
    def idx(self, mid): return self.p("index", mid)

    def meta(self): return rj(self.p("project.json"), {})
    def save_meta(self, m): wj(self.p("project.json"), m)
    def manifest(self): return rj(self.p("manifest.json"), {"media": {}})
    def save_manifest(self, m):
        m["updated"] = now()
        wj(self.p("manifest.json"), m)

    @contextlib.contextmanager
    def lock(self):
        self.dir.mkdir(parents=True, exist_ok=True)
        with open(self.p(".lock"), "w") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)

    def log(self, kind, data):
        data = {"time": now(), "kind": kind, **data}
        p = self.p("logs", "activity.jsonl")
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "a") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")

    def local_file(self, entry):
        """Path to the media file on disk (cached download or local source)."""
        if entry.get("local"):
            lp = Path(entry["local"])
            return lp if lp.is_absolute() else self.dir / lp
        return None


def active_project(ref=None):
    h = home()
    if ref:
        if "/" not in ref:
            die("project reference must be <client>/<project>")
        c, n = ref.split("/", 1)
    else:
        a = rj(h / ".active.json")
        if not a:
            die("no active project: run `cvp.py new <client> <project>` or `cvp.py use <client>/<project>`")
        c, n = a["client"], a["project"]
    pr = Project(c, n)
    if not pr.p("project.json").exists():
        die(f"no project record at {pr.dir}")
    return pr


def set_active(pr):
    wj(home() / ".active.json", {"client": pr.client, "project": pr.name, "set": now()})


def tool(name):
    return shutil.which(name)
