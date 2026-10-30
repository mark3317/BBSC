# T11 — test regressions (2026-10-30)

User report: host-first wipe leaves guest spectating after reload; silent/unknown
banners still displayed; loot accessible through closed chests; summon from Dream
briefly shows host map before the second loading screen.

## Evidence

Laptop logs copied to `build/t11-logs/` (local evidence, not committed):
`bbsc-mod-20261030-044620-16652.log`: 04:51:37.809 host revived while guest dying;
04:51:37.895 wipe warp; 04:51:43.691 spectator camera turns on after reload;
04:52:12.178 spectator released only when session ends. Banner hook logs empty
text while user sees sentinel. Disassembly of unmodified eboot confirms menu
01BFFBA7 calls [RAX+138h] with resolved UTF-16 text in RDX. 055813E0 is a string
container, not a direct pointer to its short-string content. The previous
pointer/inline fallback was incorrect.

## Changes

* At the resolved-text draw call, suppress the sentinel and ?ActionEventInfo?
  (including text containing it). Redirect ONLY the virtual text call to a no-op
  using a private vtable; do not use the entry-hook skip flag in mid-function
  (its RET would leave the menu frame on the stack). Zero that banner's timer.
  Connection/departure/PvP texts continue through the original call.
* Complete spectator state after a death load has produced a healthy local
  character, before testing remote liveness. Load completion is recognized by
  generation, a loading edge, or local character replacement; always require
  readable global state, loading false and local HP > 0. Release death locks,
  boss context and camera. No teleport or forced revival is needed for a character
  already revived by its native reload.
* Remove the blanket disabled-item re-enable pass. It cannot distinguish an
  unopened chest from an item restricted only by phantom status. Keep native
  guest pickup patches and the taken/script-hidden-item cleanup.
* Summon cover requests the game's own NowLoading screen immediately and owns
  its close. It bridges the gap to the placement reload with the same UI instead
  of initial fade/map flash. Existing arrival, failure and 75-second bounds close
  it through the native close path. This UI flow requires gameplay validation,
  especially failed summons and cancellation (historical PT-4 close-handshake risk).

## Performance configuration finding

The supplied test ran with RESEARCH enabled: startup says 168/168 selected hooks,
0 omitted, and item/save research logs are present. Therefore the T10 production
trace reduction was not exercised. Disable Research logs in launcher for the FPS
comparison. Diagnostic captures remain available for troubleshooting.

## Validation

`python tools/test_perf_policy.py`: PASS, includes suppression/keep policy checks.
`git diff --check`: PASS. Build result pending.
No deployment or save modifications in this fix session. Gameplay confirmation
pending: both wipe orders, closed/open chest and ordinary ground loot, Dream-to-
field summon/cancellation, and connection/PvP banners without placeholders.
