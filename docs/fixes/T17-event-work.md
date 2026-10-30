# T17 — first event-driven work and production scan reduction

2026-10-30. User requested implementation, build and deployment to PC/laptop.

## Changes

The game tick takes one atomic pending-work mask. Boss-reward, guest-drop and
cutscene handlers run only after enqueue notifications; peer departure locks its
queue only after a notification. Producers publish under their existing queue
mutexes. Concurrent notifications survive for the next frame; a cutscene backlog
rearms itself, retaining one replay per frame. Departure notifications rearm while
global state is unavailable. Engine calls still execute on the game thread.

Scaling compares a numeric settings/count structure instead of formatting a string
every frame. Host packet revisions refresh a game-thread cache only after a packet,
removing the unchanged-frame mutex. Heartbeats still refresh the original 15 s
expiry, and guest-count/solo transitions still reconcile each frame.

ItemSurvey, StateDiff, GateWatch and SendBacklog are research-only, including their
profiling scopes. The 250 ms gift-trigger diagnostic and periodic session-shape
scan are research-only too. Functional reward, quest, loading, death, world-sync,
HP correction and journal-recovery logic stays enabled under its existing policy.
On-demand session-shape reports remain available on actual recovery transitions.

## Validation

`python tools/test_pending_work.py`: PASS. Runs extracted production C++ helpers,
packet callback, cutscene consumer and scaling handler. Four producers deliver
100,000 actions without loss/duplication; verifies cutscene deduplication and
backlog rearming, 10,000 unchanged scaling frames without a host mutex or writes,
heartbeats, exact expiry, new settings, guest counts and solo/rejoin transitions.

Existing `test_perf_policy.py`, `test_post_load_recovery.py` (15 scenarios) and
`test_follow_arrival.py`: PASS. `git diff --check`: PASS.

Code commit: `addfd08`. Standalone mod build: `exit=0`, zero warnings.
Deployed to PC and laptop with games/launchers stopped. All three files (DLL,
launcher, mod.json) verified by SHA256 in both override and active package on each
machine (12 checks). DLL SHA256:
`A539FE8AC535F3B0BA8547644B8545ACEE32AC4E6C42A6E415CF701952D1BF11`.
Previous binaries backed up beside the installed files by deploy-mod.
Research user environment is 0 on both devices; PC extra_env explicitly has
RESEARCH=0, neither extra_env/user environment disables the default BBSC profiler.
Saves, graphics settings, port and server unchanged.
No gameplay/FPS result yet. This is phase one, not a replacement of all polling.

## Gameplay test

Research logs OFF; keep the normal BBSC profiler enabled. PC host (`testHost`),
laptop guest (`test`); current saves, no rollback. Compare one minute standing
still and one minute fighting/traversing in the same area. Check guest loot,
enemy/boss health bars, death/spectator/wipe recovery, map-border follow and clean
host exit/guest return home, then reconnect and swap roles if practical. A normal
boss cutscene/reward is desirable when available, without forcing save rollback.
Collect both machines' perf/timeline logs after the user finishes.

Test run: `20261030-161747` (run.txt/current-run recorded, VPS log byte offset captured).
