"""v2 storyboards: longer, beat-locked transitions, infographics, richer grade. Durations in beats at 124 BPM.
Transitions start exactly on the beat: the outgoing shot is extended by the transition length so the grid never drifts."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
B = 60 / 124
GRADE = "eq=contrast=1.09:saturation=1.13:gamma=0.96,colorbalance=rm=0.03:bm=-0.03:rh=0.02:bh=-0.02,unsharp=5:5:0.55,vignette=angle=PI/6"
ENDGRADE = "gblur=sigma=22,eq=brightness=-0.24:saturation=0.75,vignette=angle=PI/5"
DUR = {mid: json.load(open(ROOT / "index" / mid / "index.json"))["probe"].get("duration", 0)
       for mid in [p.name for p in (ROOT / "index").iterdir() if (p / "index.json").exists()]}
G = {"programme-landscape": "mcff1ad2a", "programme-vertical": "mff746690", "mirror-landscape": "m81d20c93",
     "mirror-vertical": "mbb58ef0f", "care-landscape": "me32b8112", "care-vertical": "m28b989fb"}
BRAND = {"accent": "#D4B07A", "text": "#FFFFFF", "box": "#1A1611", "font": "Inter"}
VALUES = [("C", "Committed"), ("A", "Accountable"), ("R", "Respectful"), ("E", "Excellent")]
push = [0]


def shot(clip, tin, beats, **k):
    photo = k.pop("photo", False)
    gfx = k.pop("gfx", False)
    s = {"clip": clip, "captions": k.pop("captions", "none")}
    if not gfx:
        s["grade"] = k.pop("grade", GRADE)
        if "zoom" not in k:  # alternate gentle push-in / pull-out for constant movement
            push[0] ^= 1
            k["zoom"], k["zoom_to"] = (1.0, 1.07) if push[0] else (1.07, 1.0)
    if photo:
        s["dur"] = round(beats * B, 3)
    else:
        sp = k.get("speed", 1.0)
        s["in"], s["out"] = tin, round(tin + beats * B * sp, 3)
    s.setdefault("audio_gain_db", -40 if gfx else -14)
    s.update(k)
    return s


def tr(kind, d):
    return {"transition": kind, "transition_dur": d}


def ov(text, style="hook", start=0.1, dur=1.8, **k):
    return {"text": text, "style": style, "start": start, "dur": dur, **k}


def sfx(name, at=0.0, g=-10, dur=None):
    x = {"file": f"sfx/sx-{name}.wav", "at": at, "gain_db": g}
    if dur:
        x["dur"] = dur
    return x


def value_ov(i, vert):
    l, w = VALUES[i]
    big, small = (240, 128) if vert else (200, 110)
    return ov(f"{{\\c&H7AB0D4&\\fs{big}}}{l}\\N{{\\c&HFFFFFF&\\fs{small}}}{w}", "kinetic", 0.15, 3.0, anim="pop")


WHIP = [sfx("whoosh-cinematic", 0.0, -11, 0.9)]
SOFT = [sfx("whoosh-soft", 0.0, -13, 0.7)]


def finish(S):
    """Extend the outgoing shot by each transition so transitions start on the beat."""
    for i in range(1, len(S)):
        td = S[i].get("transition_dur", 0) if S[i].get("transition", "cut") != "cut" else 0
        if not td:
            continue
        p = S[i - 1]
        if "dur" in p:
            p["dur"] = round(p["dur"] + td, 3)
        else:
            sp = p.get("speed", 1.0)
            if p["out"] + td * sp <= DUR[p["clip"]] - 0.05:
                p["out"] = round(p["out"] + td * sp, 3)
            else:
                p["in"] = round(p["in"] - td * sp, 3)
    return S


def landscape():
    S = []
    # HOOK (8)
    S.append(shot("m53a9b5ec", 6.0, 4, zoom=1.0, zoom_to=1.1, purpose="hook: ONE HEART shirts", sfx=[sfx("impact-bass-2", 0.0, -6)],
                  overlay=[ov("ONE HEART.", "hook", 0.05, 1.85, highlight=["HEART."])]))
    S.append(shot("mc76fc6a2", 44.0, 4, focus=[0.55, 0.55], purpose="hook: Team 2 cheer", **tr("flash", 0.15), sfx=WH(),
                  overlay=[ov("ONE MISSION.", "hook", 0.1, 1.75, highlight=["MISSION."])]))
    # INTRO (32)
    S.append(shot("m298798b7", 1.0, 6, focus=[0.4, 0.5], focus_to=[0.6, 0.5], purpose="arrival: lake venue", **tr("dissolve", 0.5)))
    S.append(shot("mf764b2dc", 0.1, 4, zoom=1.0, zoom_to=1.0, focus=[1.0, 0.5], purpose="arrival: LET'S GO", **tr("zoom", 0.25), sfx=SOFT))
    S.append(shot("m33d8b7ec", 4.3, 6, zoom=1.35, zoom_to=1.42, focus=[0.6, 0.5], audio_gain_db=0, speech=True, purpose="trainer: Muhaini",
                  captions=[{"text": "We have to have action.", "start": 0.12, "end": 2.75}], dialogue="We have to have action. (verify)",
                  overlay=[ov("Muhaini\\NTrainer", "lower", 0.3, 2.4, anim="slide")]))
    S.append(shot("m33d8b7ec", 13.4, 4, purpose="title: C.A.R.E IN ACTION screen",
                  overlay=[ov("KPJ Healthcare Teambuilding\\N27.11.2026", "lower", 0.15, 1.75, anim="slide")]))
    S.append(shot(G["programme-landscape"], 0, 12, gfx=True, purpose="infographic: the programme (from session screens)", **tr("slide", 0.3),
                  sfx=WHIP + [sfx("pop", 3 * B), sfx("pop-2", 5 * B), sfx("pop-3", 7 * B)]))
    # BUILD (16)
    S.append(shot("m33d8b7ec", 20.0, 2, speed=1.5, purpose="sessions: hands up", **tr("whip", 0.2), sfx=WHIP))
    S.append(shot("m6dda40ef", 10.0, 2, purpose="sessions: tables"))
    S.append(shot("mc427ad1e", 0, 2, photo=True, zoom=1.0, zoom_to=1.1, purpose="sessions: ARE YOU READY? paper planes"))
    S.append(shot("mcb2640b4", 0.3, 2, focus=[0.5, 0.33], purpose="sessions: 'Your team needs an identity'"))
    S.append(shot(G["care-landscape"], 0, 8, gfx=True, purpose="infographic: C.A.R.E reveal", **tr("whip", 0.2),
                  sfx=WHIP + [sfx("pop", 0.0), sfx("pop-2", B), sfx("pop-3", 2 * B), sfx("pop-4", 3 * B), sfx("sparkle", 6 * B, -12)]))
    # DROP (52): C 12, A 16, R 12, E 12
    S.append(shot("m89c1e919", 4.0, 4, purpose="C: drawing the tribe banner", **tr("flash", 0.15), overlay=[value_ov(0, False)],
                  sfx=[sfx("pop", 0.15)], music_cue="drop"))
    S.append(shot("ma3abb7f7", 8.0, 4, speed=1.5, purpose="C: all hands in"))
    S.append(shot("m4ee4a2e4", 14.0, 4, purpose="C: identity takes shape"))
    S.append(shot("m7904d089", 30.0, 4, zoom=1.08, zoom_to=1.15, purpose="A: writing on the Reflection Mirror", **tr("whip", 0.2),
                  overlay=[value_ov(1, False)], sfx=WHIP + [sfx("pop-2", 0.15)]))
    S.append(shot(G["mirror-landscape"], 0, 12, gfx=True, purpose="infographic: the Reflection Mirror questions (from screen)", **tr("slide", 0.3),
                  sfx=SOFT + [sfx("click-hi", 3 * B, -12), sfx("click-hi", 5 * B, -12), sfx("click-hi", 7 * B, -12)]))
    S.append(shot("m5e0e4909", 2.0, 4, audio_gain_db=-8, purpose="R: circle game", **tr("whip", 0.2), overlay=[value_ov(2, False)],
                  sfx=WHIP + [sfx("pop-3", 0.15)]))
    S.append(shot("m62ddce82", 28.0, 4, focus=[0.5, 0.4], purpose="R: listening"))
    S.append(shot("mce8eb1c3", 24.0, 4, speed=1.5, purpose="R: everyone moves together"))
    S.append(shot("m792b212d", 20.0, 4, zoom=1.08, zoom_to=1.15, purpose="E: Lion team anthem", **tr("whip", 0.2), overlay=[value_ov(3, False)],
                  sfx=WHIP + [sfx("pop-4", 0.15)]))
    S.append(shot("mb8f104bd", 3.6, 4, zoom=1.1, zoom_to=1.04, audio_gain_db=-4, speech=True, purpose="E: One Heart Mission",
                  captions=[{"text": "One Heart Mission!", "start": 0.12, "end": 1.95}]))
    for k, (cid, pp) in enumerate([("m466f6022", "pop"), ("me8f3bee0", "pop-2"), ("m7ff99f4a", "pop-3"), ("mb0f460d5", "pop-4")]):
        S.append(shot(cid, 0, 1, photo=True, zoom=1.0, zoom_to=1.12, focus=[0.5, 0.22], purpose=f"E: team creations board {k + 1}", sfx=[sfx(pp, 0.02, -11)],
                      overlay=[ov("Team creations", "callout", 0.05, 1.85, anim="slide", pos=[960, 940])] if k == 0 else []))
    # ANTHEM (24): Team 3 line, continuous audio across punch-ins
    caps = [[{"text": "We are the shield", "start": 0.1, "end": 2.9}, {"text": "that protect our nation", "start": 2.9, "end": 3.87}],
            [{"text": "that protect our nation", "start": 0.0, "end": 3.2}, {"text": "with respect", "start": 3.2, "end": 3.87}],
            [{"text": "with respect and care.", "start": 0.0, "end": 3.4}]]
    for j, (z, f) in enumerate([((1.0, 1.06), [0.5, 0.5]), ((1.3, 1.36), [0.5, 0.6]), ((1.12, 1.2), [0.45, 0.5])]):
        extra = tr("dissolve", 0.5) if j == 0 else {}
        S.append(shot("m5fa6dffe", round(23.05 + j * 8 * B, 3), 8, zoom=z[0], zoom_to=z[1], focus=f, audio_gain_db=0, speech=True,
                      captions=caps[j], purpose="anthem: Team 3 'Respect Shield'", **extra))
    # FINALE (32)
    S.append(shot("mc76fc6a2", 56.0, 4, purpose="finale: Team 2 celebrates", **tr("flash", 0.15), sfx=[sfx("impact-bass-2", 0.0, -8)], music_cue="drop 2"))
    S.append(shot("m506a5205", 0, 2, photo=True, zoom=1.0, zoom_to=1.1, purpose="finale: paper-plane laughter"))
    S.append(shot("m1598a19c", 0, 2, photo=True, zoom=1.1, zoom_to=1.0, purpose="finale: paper-plane laughter"))
    S.append(shot("m50434b59", 9.0, 4, focus=[0.6, 0.5], purpose="finale: paper planes up"))
    S.append(shot("mcd305bb8", 44.0, 4, purpose="finale: hearts banner"))
    S.append(shot("m53a9b5ec", 0.2, 4, purpose="finale: everyone, every banner", **tr("zoom", 0.25), sfx=SOFT,
                  overlay=[ov("ONE TEAM. ONE HEART.", "kinetic", 0.1, 1.8, highlight=["ONE HEART."])]))
    S.append(shot("m53a9b5ec", 6.4, 4, purpose="finale: close-up joy"))
    S.append(shot("mb95fb3a1", 0, 4, photo=True, zoom=1.12, zoom_to=1.0, purpose="finale: the photo"))
    S.append(shot("m53a9b5ec", 19.6, 4, purpose="finale: selfie energy"))
    S.append(shot("m192e86db", 0, 16, photo=True, grade=ENDGRADE, zoom=1.0, zoom_to=1.06, **tr("dissolve", 0.6), purpose="end card",
                  sfx=[sfx("sparkle", 0.4, -10)],
                  overlay=[ov("C.A.R.E in Action", "kinetic", 0.6, 6.6, pos=[960, 600], anim="fade", highlight=["C.A.R.E"]),
                           ov("Committed · Accountable · Respectful · Excellent", "callout", 1.0, 6.2, pos=[960, 740], anim="fade"),
                           ov("27.11.2026", "callout", 1.2, 6.0, pos=[960, 830], anim="fade")]))
    return {"format": "landscape", "fps": 30, "brand": BRAND, "captions": {"enabled": True, "max_words": 4, "size": 62}, "loudness": -14,
            "music": {"track": "care-anthem-v2-landscape", "start": 0, "gain_db": -9, "fade_out": 2.5, "duck_threshold": 0.03, "duck_ratio": 6},
            "logos": [{"file": "brand/kpj-logo-white.png", "start": None, "dur": 6.4, "width": 820, "pos": [960, 400], "fade": 0.5}],
            "shots": finish(S)}


def vertical():
    S = []
    S.append(shot("m53a9b5ec", 6.0, 4, zoom=1.0, zoom_to=1.1, purpose="hook", sfx=[sfx("impact-bass-2", 0.0, -6)],
                  overlay=[ov("ONE HEART.\\NONE MISSION.", "hook", 0.05, 1.85, highlight=["HEART.", "MISSION."], pos=[540, 400])]))
    S.append(shot("ma2b24d1f", 0.2, 4, purpose="title: stage", **tr("flash", 0.15), sfx=SOFT,
                  overlay=[ov("KPJ Healthcare\\NTeambuilding · 27.11.2026", "lower", 0.1, 1.8, anim="slide")]))
    S.append(shot("m33d8b7ec", 4.3, 4, zoom=1.2, zoom_to=1.26, focus=[0.47, 0.5], audio_gain_db=0, speech=True, purpose="trainer: Muhaini",
                  captions=[{"text": "We have to have action.", "start": 0.12, "end": 1.94}], overlay=[ov("Muhaini\\NTrainer", "lower", 0.1, 1.8, anim="slide")]))
    S.append(shot(G["care-vertical"], 0, 8, gfx=True, purpose="infographic: C.A.R.E reveal", **tr("whip", 0.2),
                  sfx=WHIP + [sfx("pop", 0.0), sfx("pop-2", B), sfx("pop-3", 2 * B), sfx("pop-4", 3 * B), sfx("sparkle", 6 * B, -12)]))
    # DROP (48): C 8, A 16, R 12, E 12
    S.append(shot("m89c1e919", 4.0, 4, purpose="C: drawing the tribe banner", **tr("flash", 0.15), overlay=[value_ov(0, True)], sfx=[sfx("pop", 0.15)], music_cue="drop"))
    S.append(shot("ma3abb7f7", 8.0, 4, speed=1.5, purpose="C: all hands in"))
    S.append(shot("m7904d089", 30.0, 4, zoom=1.1, zoom_to=1.16, focus=[0.42, 0.5], purpose="A: Reflection Mirror", **tr("whip", 0.2),
                  overlay=[value_ov(1, True)], sfx=WHIP + [sfx("pop-2", 0.15)]))
    S.append(shot(G["mirror-vertical"], 0, 12, gfx=True, purpose="infographic: Reflection Mirror questions", **tr("slide", 0.3),
                  sfx=SOFT + [sfx("click-hi", 3 * B, -12), sfx("click-hi", 5 * B, -12), sfx("click-hi", 7 * B, -12)]))
    S.append(shot("meb4f6112", 8.0, 4, audio_gain_db=-8, purpose="R: circle game", **tr("whip", 0.2), overlay=[value_ov(2, True)], sfx=WHIP + [sfx("pop-3", 0.15)]))
    S.append(shot("m62ddce82", 28.0, 4, focus=[0.5, 0.4], purpose="R: listening"))
    S.append(shot("m440343d6", 18.0, 4, speed=1.5, purpose="R: moving together"))
    S.append(shot("mb8f104bd", 3.6, 4, zoom=1.05, zoom_to=1.12, focus=[0.45, 0.5], audio_gain_db=-4, speech=True, purpose="E: One Heart Mission",
                  **tr("whip", 0.2), captions=[{"text": "One Heart Mission!", "start": 0.12, "end": 1.95}], overlay=[value_ov(3, True)],
                  sfx=WHIP + [sfx("pop-4", 0.15)]))
    S.append(shot("m792b212d", 20.0, 4, focus=[0.45, 0.5], purpose="E: Lion team anthem"))
    for k, (cid, pp) in enumerate([("m466f6022", "pop"), ("me8f3bee0", "pop-2"), ("m7ff99f4a", "pop-3"), ("mb0f460d5", "pop-4")]):
        S.append(shot(cid, 0, 1, photo=True, zoom=1.0, zoom_to=1.12, purpose=f"E: team creations board {k + 1}", sfx=[sfx(pp, 0.02, -11)],
                      overlay=[ov("Team creations", "callout", 0.05, 1.85, anim="slide", pos=[540, 1300])] if k == 0 else []))
    # LIFT (4) + FINALE (12)
    S.append(shot("m506a5205", 0, 2, photo=True, zoom=1.0, zoom_to=1.12, focus=[0.45, 0.5], purpose="lift: paper-plane laughter", sfx=[sfx("riser", 0.0, -14, 1.9)]))
    S.append(shot("m1598a19c", 0, 2, photo=True, zoom=1.12, zoom_to=1.0, focus=[0.5, 0.5], purpose="lift: laughter"))
    S.append(shot("mc76fc6a2", 56.0, 4, focus=[0.55, 0.5], purpose="finale: Team 2", **tr("flash", 0.15), sfx=[sfx("impact-bass-2", 0.0, -8)]))
    S.append(shot("m53a9b5ec", 19.6, 4, purpose="finale: selfie energy"))
    S.append(shot("m53a9b5ec", 0.2, 4, purpose="finale: everyone", overlay=[ov("ONE TEAM.\\NONE HEART.", "kinetic", 0.1, 1.8, highlight=["ONE HEART."])]))
    S.append(shot("m3917430d", 0, 16, photo=True, grade=ENDGRADE, zoom=1.0, zoom_to=1.06, **tr("dissolve", 0.5), purpose="end card",
                  sfx=[sfx("sparkle", 0.3, -10)],
                  overlay=[ov("C.A.R.E\\Nin Action", "kinetic", 0.5, 6.6, pos=[540, 900], anim="fade", highlight=["C.A.R.E"]),
                           ov("Committed · Accountable\\NRespectful · Excellent", "callout", 0.9, 6.2, pos=[540, 1110], anim="fade"),
                           ov("27.11.2026", "callout", 1.1, 6.0, pos=[540, 1250], anim="fade")]))
    return {"format": "vertical", "fps": 30, "brand": BRAND, "captions": {"enabled": True, "max_words": 3, "y": 1200}, "loudness": -14,
            "music": {"track": "care-anthem-v2-vertical", "start": 0, "gain_db": -9, "fade_out": 2.0, "duck_threshold": 0.03, "duck_ratio": 6},
            "logos": [{"file": "brand/kpj-logo-white.png", "start": None, "dur": 6.4, "width": 760, "pos": [540, 700], "fade": 0.5}],
            "shots": finish(S)}


def WH():
    return [sfx("whoosh", 0.0, -12, 0.8)]


if __name__ == "__main__":
    out = Path(sys.argv[1])
    for sb in (landscape(), vertical()):
        last = sb["shots"][-1]
        t = sum((s["out"] - s["in"]) / s.get("speed", 1) if "in" in s else s["dur"] for s in sb["shots"][:-1])
        t -= sum(s.get("transition_dur", 0) for s in sb["shots"][1:] if s.get("transition", "cut") != "cut")
        sb["logos"][0]["start"] = round(t + 0.4, 3)
        json.dump(sb, open(out / f"sb3-{sb['format']}.json", "w"), indent=1)
        print(sb["format"], len(sb["shots"]), "shots, end card at", round(t, 2))
