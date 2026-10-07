#!/usr/bin/env python3
"""gate_check.py — the round-228 gate verdict from one civtest console log, so progress is never read from the
"N building(s)" line (staged plots) again (D-C1006-WAGONS).

Usage: gate_check.py [LOG]   (default: the newest _bds/logs/civtest-*.txt)

Checks (each printed PASS / FAIL / WAIT with its number):
  wagons    the settlers' wagons carry materials and come AFTER "founded" (the stalled-start bug)
  economy   a ledger section is saved and [CIV-MOOD] census lines appear (the economy and the census run)
  built     buildings FINISHED (stage 4) at "village built" > 0, and the last evo step's finished count
  people    the census size (n) of the last [CIV-MOOD] line > 0
  watch     watchmen on duty during the night test (onDuty > 0 in any sample)
  health    0 Hang, 0 Crash
"""
import json
import re
import sys
from pathlib import Path

LOGS = Path("/home/claude/_bds/logs")


def newest_log():
    return max(LOGS.glob("civtest-*.txt"), key=lambda p: p.stat().st_mtime)


def civtest_records(text):
    """Every [CIVTEST] JSON record in console order (lines that fail to parse are skipped)."""
    out = []
    for m in re.finditer(r"\[CIVTEST\] (\{.*)", text):
        try:
            out.append(json.loads(m.group(1)))
        except json.JSONDecodeError:
            continue
    return out


def main():
    log = Path(sys.argv[1]) if len(sys.argv) > 1 else newest_log()
    text = log.read_text(errors="ignore").replace("\x00", "")
    recs = civtest_records(text)
    verdicts = []

    founded_at = text.find("founded on the knoll")
    wag = re.search(r"the settlers' wagons: ([^\"]*?), food for", text)
    if not wag:
        verdicts.append(("wagons", "WAIT", "no wagons line yet"))
    else:
        mats, after = wag.group(1).strip(), founded_at != -1 and wag.start() > founded_at
        ok = bool(mats) and after
        verdicts.append(("wagons", "PASS" if ok else "FAIL", f"materials [{mats[:80]}] after-founded={after}"))

    mood = [json.loads(m.group(1)) for m in re.finditer(r"\[CIV-MOOD\] (\{.*)", text)]
    ledger = re.findall(r'"pw:civ:st:1:ledger":(\d+)', text)
    econ_ok = bool(mood) and bool(ledger)
    verdicts.append(("economy", "PASS" if econ_ok else ("WAIT" if not recs else "FAIL"),
                     f"{len(mood)} CIV-MOOD lines, ledger section {ledger[-1] if ledger else 'absent'} B"))

    evo = [r for r in recs if r.get("step") == "evo"]
    vb = next((r for r in evo if r.get("expect") == "village built"), None)
    if vb is None:
        verdicts.append(("built", "WAIT", "no 'village built' step yet"))
    else:
        last = evo[-1]
        verdicts.append(("built", "PASS" if vb["finished"] > 0 else "FAIL",
                         f"village built {vb['finished']}/{vb['plots']}; last '{last['expect']}' {last['finished']}/{last['plots']}"))

    if mood:
        verdicts.append(("people", "PASS" if mood[-1].get("n", 0) > 0 else "FAIL", f"day {mood[-1].get('day')} n {mood[-1].get('n')}"))
    else:
        verdicts.append(("people", "WAIT", "no census line yet"))

    watch = next((r for r in recs if r.get("step") == "watch"), None)
    if watch is None:
        verdicts.append(("watch", "WAIT", "night test not reached"))
    else:
        duty = max([s.get("watch", {}).get("onDuty", 0) for s in watch.get("samples", [])] + [0])
        rounds = max([s.get("watch", {}).get("rounds", 0) for s in watch.get("samples", [])] + [0])
        verdicts.append(("watch", "PASS" if duty > 0 else "FAIL", f"onDuty max {duty}, rounds {rounds}"))

    hangs, crash = text.count("Hang"), text.count("Crash")
    verdicts.append(("health", "PASS" if hangs == 0 and crash == 0 else "FAIL", f"Hang {hangs}, Crash {crash}"))

    print(log.name)
    for name, v, detail in verdicts:
        print(f"  {name:8s} {v:4s}  {detail}")


if __name__ == "__main__":
    main()
