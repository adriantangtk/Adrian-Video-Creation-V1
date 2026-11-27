"""Project-specific storyboard builder for KPJ C.A.R.E in Action (durations in beats at 124 BPM)."""
import json, sys
B = 60 / 124
GRADE = "eq=contrast=1.06:saturation=1.08:gamma=0.97,colorbalance=rm=0.02:bm=-0.02"
ENDGRADE = "gblur=sigma=22,eq=brightness=-0.22:saturation=0.75"
def shot(clip, tin, beats, **k):
    s = {"clip": clip, "grade": k.pop("grade", GRADE), "captions": k.pop("captions", "none")}
    if k.pop("photo", False):
        s["dur"] = round(beats * B, 3)
    else:
        sp = k.get("speed", 1.0)
        s["in"], s["out"] = tin, round(tin + beats * B * sp, 3)
    s.setdefault("audio_gain_db", -14)
    s.update(k)
    return s
def ov(text, style="hook", start=0.1, dur=1.8, **k):
    return {"text": text, "style": style, "start": start, "dur": dur, **k}
WH = {"file": "sfx/sx-whoosh-soft.wav", "at": -0.12, "gain_db": -12, "dur": 0.6}
def pop(n=1, at=0.1): return {"file": f"sfx/sx-pop{'' if n == 1 else '-' + str(n)}.wav", "at": at, "gain_db": -10}
BRAND = {"accent": "#D4B07A", "text": "#FFFFFF", "box": "#1A1611", "font": "Inter"}
CAP = {"enabled": True, "max_words": 4}
VALUES = [("C", "Committed"), ("A", "Accountable"), ("R", "Respectful"), ("E", "Excellent")]

def value_ov(i, vert):
    l, w = VALUES[i]
    big = 240 if vert else 200
    small = 128 if vert else 110  # explicit reset instead of \\r so the pop animation still applies
    return ov(f"{{\\c&H7AB0D4&\\fs{big}}}{l}\\N{{\\c&HFFFFFF&\\fs{small}}}{w}", "kinetic", 0.15, 3.4, anim="pop")

def landscape():
    S = []
    S.append(shot("m53a9b5ec", 6.0, 4, zoom=1.0, zoom_to=1.08, purpose="hook: group close-up waving, ONE HEART shirts",
                  overlay=[ov("ONE HEART.", "hook", 0.05, 1.85, highlight=["HEART"])], sfx=[{"file": "sfx/sx-impact-bass-2.wav", "at": 0.0, "gain_db": -6}]))
    S.append(shot("mc76fc6a2", 44.0, 4, zoom=1.1, focus=[0.55, 0.55], purpose="hook: Team 2 with C.A.R.E heart banner",
                  overlay=[ov("ONE MISSION.", "hook", 0.05, 1.85, highlight=["MISSION"])], sfx=[WH]))
    S.append(shot("m298798b7", 1.0, 3, purpose="arrival: venue by the lake", sfx=[WH]))
    S.append(shot("mf764b2dc", 0.3, 3, zoom=1.0, zoom_to=1.05, focus=[0.78, 0.5], purpose="arrival: LET'S GO screen"))
    S.append(shot("m33d8b7ec", 4.3, 6, zoom=1.35, focus=[0.6, 0.5], audio_gain_db=0, speech=True,
                  captions=[{"text": "We have to have action.", "start": 0.12, "end": 2.75}],
                  overlay=[ov("Muhaini\\NTrainer", "lower", 0.3, 2.5, anim="slide")], purpose="trainer: Muhaini sets the tone",
                  dialogue="We have to have action. (Muhaini; machine transcript, verify)"))
    S.append(shot("m33d8b7ec", 13.4, 4, zoom=1.0, zoom_to=1.06, purpose="title: C.A.R.E IN ACTION screen",
                  overlay=[ov("KPJ Healthcare Teambuilding\\N27.11.2026", "lower", 0.15, 1.75, anim="slide")]))
    S.append(shot("m33d8b7ec", 20.0, 4, purpose="sessions: room engaged", sfx=[WH]))
    S.append(shot("m6dda40ef", 10.0, 4, zoom=1.05, purpose="sessions: tables at work"))
    S.append(shot("m7904d089", 0.5, 4, zoom=1.0, zoom_to=1.08, purpose="sessions: Reflection Mirror brief on screen"))
    S.append(shot("m7bc17175", 22.0, 4, purpose="sessions: wide room energy"))
    # C.A.R.E values on the drop (8 beats each)
    S.append(shot("m89c1e919", 4.0, 4, focus=[0.5, 0.5], purpose="C: teams drawing their tribe banner",
                  overlay=[value_ov(0, False)], sfx=[WH, pop(1, 0.15)], music_cue="drop"))
    S.append(shot("ma3abb7f7", 8.0, 4, focus=[0.5, 0.45], purpose="C: commitment to the team identity"))
    S.append(shot("m7904d089", 30.0, 4, zoom=1.1, purpose="A: teams writing on the Reflection Mirror", overlay=[value_ov(1, False)], sfx=[WH, pop(2, 0.15)]))
    S.append(shot("m93302ffb", 0, 4, photo=True, zoom=1.0, zoom_to=1.1, purpose="A: Reflection Mirror sticky notes"))
    S.append(shot("m5e0e4909", 2.0, 4, purpose="R: circle game, everyone in", overlay=[value_ov(2, False)], sfx=[WH, pop(3, 0.15)], audio_gain_db=-8))
    S.append(shot("m62ddce82", 28.0, 4, focus=[0.5, 0.4], purpose="R: listening to a teammate"))
    S.append(shot("m792b212d", 20.0, 4, zoom=1.1, purpose="E: Lion team performs the anthem", overlay=[value_ov(3, False)], sfx=[WH, pop(4, 0.15)]))
    S.append(shot("mb8f104bd", 3.6, 4, zoom=1.1, audio_gain_db=-4, speech=True, purpose="E: One Heart Mission",
                  captions=[{"text": "One Heart Mission!", "start": 0.12, "end": 1.95}], dialogue="1 Heart Mission! (machine transcript, verify)"))
    # anthem moment: Team 3 'Respect Shield' line, continuous audio across punch-ins
    for j, (z, f) in enumerate([(1.0, [0.5, 0.5]), (1.3, [0.5, 0.6]), (1.12, [0.45, 0.5])]):
        tin = round(23.05 + j * 8 * B, 3)
        caps = [[{"text": "We are the shield", "start": 0.1, "end": 2.9}, {"text": "that protect our nation", "start": 2.9, "end": 3.87}],
                [{"text": "that protect our nation", "start": 0.0, "end": 3.2}, {"text": "with respect", "start": 3.2, "end": 3.87}],
                [{"text": "with respect and care.", "start": 0.0, "end": 3.4}]][j]
        S.append(shot("m5fa6dffe", tin, 8, zoom=z, focus=f, audio_gain_db=0, speech=True, captions=caps,
                      purpose="anthem: Team 3 'Respect Shield'", dialogue="We are the shield that protect our nation with respect and care. (verify)",
                      music_cue="breakdown" if j == 0 else "lift" if j == 2 else ""))
    S.append(shot("mc76fc6a2", 56.0, 4, zoom=1.1, purpose="finale: Team 2 celebrates", sfx=[WH], music_cue="drop 2"))
    S.append(shot("m2c2c4614", 26.0, 4, purpose="finale: crowd cheering"))
    S.append(shot("mcd305bb8", 44.0, 4, zoom=1.1, purpose="finale: hearts banner"))
    S.append(shot("m53a9b5ec", 0.2, 4, zoom=1.0, zoom_to=1.06, purpose="finale: everyone, every banner",
                  overlay=[ov("ONE TEAM. ONE HEART.", "kinetic", 0.1, 1.8, highlight=["ONE HEART."])]))
    S.append(shot("m53a9b5ec", 6.4, 4, purpose="finale: close-up joy"))
    S.append(shot("m53a9b5ec", 19.6, 4, zoom=1.0, zoom_to=1.08, purpose="finale: selfie energy"))
    S.append(shot("m192e86db", 0, 15, photo=True, grade=ENDGRADE, zoom=1.0, zoom_to=1.06, transition="dissolve", transition_dur=0.5,
                  purpose="end card", sfx=[{"file": "sfx/sx-sparkle.wav", "at": 0.4, "gain_db": -10}],
                  overlay=[ov("C.A.R.E in Action", "kinetic", 0.6, 6.2, pos=[960, 600], anim="fade", highlight=["C.A.R.E"]),
                           ov("Committed · Accountable · Respectful · Excellent", "callout", 1.0, 5.8, pos=[960, 740], anim="fade"),
                           ov("27.11.2026", "callout", 1.2, 5.6, pos=[960, 830], anim="fade")]))
    return {"format": "landscape", "fps": 30, "brand": BRAND, "captions": dict(CAP, size=62), "loudness": -14,
            "music": {"track": "care-anthem-landscape", "start": 0, "gain_db": -9, "fade_out": 2.5, "duck_threshold": 0.03, "duck_ratio": 6},
            "logos": [{"file": "brand/kpj-logo-white.png", "start": None, "dur": 6.0, "width": 820, "pos": [960, 400], "fade": 0.5}],
            "shots": S}

def vertical():
    S = []
    S.append(shot("m53a9b5ec", 6.0, 4, zoom=1.0, zoom_to=1.1, focus=[0.5, 0.5], purpose="hook: ONE HEART shirts waving",
                  overlay=[ov("ONE HEART.\\NONE MISSION.", "hook", 0.05, 1.85, highlight=["HEART.", "MISSION."], pos=[540, 400])],
                  sfx=[{"file": "sfx/sx-impact-bass-2.wav", "at": 0.0, "gain_db": -6}]))
    S.append(shot("ma2b24d1f", 0.2, 4, zoom=1.0, zoom_to=1.08, purpose="title: C.A.R.E in Action stage", sfx=[WH],
                  overlay=[ov("KPJ Healthcare\\NTeambuilding · 27.11.2026", "lower", 0.1, 1.8, anim="slide")]))
    S.append(shot("m33d8b7ec", 4.3, 4, zoom=1.2, focus=[0.47, 0.5], audio_gain_db=0, speech=True,
                  captions=[{"text": "We have to have action.", "start": 0.12, "end": 1.94}],
                  overlay=[ov("Muhaini\\NTrainer", "lower", 0.1, 1.8, anim="slide")], purpose="trainer: Muhaini"))
    S.append(shot("md9a4245e", 6.0, 4, purpose="sessions: the room"))
    S.append(shot("m89c1e919", 4.0, 4, purpose="C: drawing the tribe banner", overlay=[value_ov(0, True)], sfx=[WH, pop(1, 0.15)], music_cue="drop"))
    S.append(shot("m4ee4a2e4", 20.0, 4, purpose="C: heads down, all in"))
    S.append(shot("m7904d089", 30.0, 4, zoom=1.1, focus=[0.42, 0.5], purpose="A: teams writing on the Reflection Mirror", overlay=[value_ov(1, True)], sfx=[WH, pop(2, 0.15)]))
    S.append(shot("m2106bc1c", 28.0, 4, purpose="A: owning the takeaways"))
    S.append(shot("meb4f6112", 8.0, 4, purpose="R: circle game", overlay=[value_ov(2, True)], sfx=[WH, pop(3, 0.15)], audio_gain_db=-8))
    S.append(shot("m62ddce82", 28.0, 4, focus=[0.5, 0.4], purpose="R: one voice, everyone listening"))
    S.append(shot("mb8f104bd", 3.6, 4, zoom=1.05, focus=[0.45, 0.5], audio_gain_db=-4, speech=True, purpose="E: One Heart Mission",
                  captions=[{"text": "One Heart Mission!", "start": 0.12, "end": 1.95}], overlay=[value_ov(3, True)], sfx=[WH, pop(4, 0.15)]))
    S.append(shot("m1dd4bda8", 18.0, 4, purpose="E: the room cheers"))
    S.append(shot("m53a9b5ec", 0.2, 15, grade=ENDGRADE, zoom=1.0, zoom_to=1.06, focus=[0.5, 0.5], transition="dissolve", transition_dur=0.4,
                  purpose="end card over group photo", sfx=[{"file": "sfx/sx-sparkle.wav", "at": 0.3, "gain_db": -10}], audio_gain_db=-20,
                  overlay=[ov("C.A.R.E\\Nin Action", "kinetic", 0.5, 6.2, pos=[540, 900], anim="fade", highlight=["C.A.R.E"]),
                           ov("Committed · Accountable\\NRespectful · Excellent", "callout", 0.9, 5.8, pos=[540, 1110], anim="fade"),
                           ov("27.11.2026", "callout", 1.1, 5.6, pos=[540, 1250], anim="fade")]))
    return {"format": "vertical", "fps": 30, "brand": BRAND, "captions": dict(CAP, max_words=3, y=1200), "loudness": -14,
            "music": {"track": "care-anthem-vertical", "start": 0, "gain_db": -9, "fade_out": 2.0, "duck_threshold": 0.03, "duck_ratio": 6},
            "logos": [{"file": "brand/kpj-logo-white.png", "start": None, "dur": 6.0, "width": 760, "pos": [540, 700], "fade": 0.5}],
            "shots": S}

for sb in (landscape(), vertical()):
    # logo appears with the end card: start = end-card start + 0.3 (sum of earlier beats)
    t = sum((s["out"] - s["in"]) / s.get("speed", 1) if "in" in s else s["dur"] for s in sb["shots"][:-1]) - sb["shots"][-1].get("transition_dur", 0)
    sb["logos"][0]["start"] = round(t + 0.3, 3)
    json.dump(sb, open(f"{sys.argv[1]}/sb-{sb['format']}.json", "w"), indent=1)
    print(sb["format"], len(sb["shots"]), "shots, end card at", round(t, 2))
