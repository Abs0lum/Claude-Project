# LESSON CANDIDATES — the CIVITAS city round, 2026-10-04 (for your approval before they enter FOUNDATION)

Each line is a candidate. It becomes a lesson only with your yes (Lesson Supersession, MANUAL §15). Evidence: the RESULTS
entry named (`_docs/RESULTS-AND-IDEAS-2026-10-04.md`) and the journal D-C554 / D-C555.

## Engine and API facts (proven on the server, BDS 1.26.52)
1. **`minecraft:behavior.follow_mob` follows ANY mob that passes its filters** — with several leads in range, a villager
   follows another villager's lead (R-31). Personal following works with an int entity property on the target and an
   `int_property` filter (subject other, operator ==) in one component group per slot (R-31: 224 arrived / 25 stuck vs
   12 / 78).
2. **A ticking area is capped at 100 chunks, counted on chunk boundaries**: a 160-block box that does not start on a
   chunk edge spans 11 × 11 = 121 chunks and is refused WITHOUT an error (R-30). Lay boxes on chunk edges; check
   `successCount`.
3. **A follow target embedded in a solid block stalls the follower** (R-35: route heights one below a road surface).

## Method
4. **A resumable budgeted search must persist EVERY loop index that can outlast the budget**, or it livelocks on its
   first slow inner case (E3 / R-22: the side-street scan never passed its first half in six runs).
5. **A guard that never fires can hide a deeper fault**: before removing a forced fallback, prove the normal path ever
   succeeds (R-30: the forced sewer survey hid a silent ticking-area refusal — and ran on unloaded land).
6. **A queue another design ordered on purpose is not mine to re-rank wholesale**: promote the one item that needs it
   (R-40: a prestige-first rank starved a founding of its farm, quarry and lumberyard).
7. **A list that is written but never read is a silent loss** (E7 / R-36: civic works without room were lost forever).
8. **Vary the test site on purpose, and keep one fixed site for comparisons** (R-34 / R-41: a cramped site exposed the
   builders' deadlock the roomy ones hid).
9. **Measure before optimising the server**: a per-interval profiler showed the costs were the keepers' routes, the
   work searches' occupied set and the schedule's legs — not the walk beat (R-43 / R-45).
10. **Kill by PID only** — `pkill -f <name>` matched my own shell's command line (06:5x, exit 144). The PID rule stands.
