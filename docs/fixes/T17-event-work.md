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

## Gameplay result and crash investigation (2026-10-30)

User reports that gameplay generally works. Collected PC, laptop and VPS logs for
run `20261030-161747`; PC process 42488, laptop 16264, both built 16:15:57 with
31/31 production trace hooks (137 diagnostic hooks omitted).

PC Windows System: nvlddmkm event 153 at 16:27:49.427, then twice at
16:27:53.728/736 Moscow time. WER Application event 1001 records LiveKernelEvent
141 at 16:27:59 and archives it at 16:28:47 under
`LKD_0x141_Tdr:6_IMAGE_nvlddmkm.sys_Blackwell`. Both WER entries share report ID
91177bbe-07ff-43f0-b763-1a81588a37e8: one incident, not two crashes.
No collected application access-violation event or bb-probe crash dump.
The log names WATCHDOG-20261030-1627.dmp; it was not present in the normal app
crash-dump collection. Root cause was not established by dump analysis.

PC BBSC log ends at 16:27:49.351 in native OwnWorldStep/SkippedCleanup with a
kept-death reinsert armed; the first GPU error follows ~76 ms later. This confirms
a GPU TDR coincident with the crash, not proof of faulty GPU hardware or proof
that the mod/renderer cannot trigger it. No new queue/cache fault is evident.
Current PC bbport.ini (mtime 16:18:56, before process start 16:19:08) has
upscaler=off, frame_gen=dlss, multiplier=2; copied into the run. This is config
evidence, not a renderer initialization trace. Earlier TDRs also happened with FG
OFF, so FG is not established as a necessary cause. Settings left unchanged.

At 16:27:54 laptop receives confirmed host departure, suspends persistence and
returns scaling to solo. At 16:27:56 it requests home; at 16:28:00 own-world
restoration puts back 960 groups and applies 18 talk flags. At 16:28:05 it reaches
Central Yharnam; at 16:28:10 K2-trip-home confirms two item kinds retained. VPS
shows host connection reset, no preceding relay send failure/slow-client eviction.

Other observations: six journaled goods were restored after guest loads at
16:21:14 and 16:21:25 (K2-lost-at-load says "put back"). PC warned about loading
screen state 3 lingering 30 s after death (16:26:46). These need tracking separately
from the GPU incident; no visible softlock was reported. Echo HUD observers report
"never ran" in production, so that warning alone is not proof of a broken HUD.

Profiler: 47 PC ten-second samples, median 59.7 game ticks/s, 58.3-60.0 range;
median reported total BBSC overhead 1.474 ms/frame. Laptop: 48 samples including
loads, median 54.2 ticks/s, median overhead 3.4105 ms/frame. These are game-thread
rates, not FG display FPS, and do not quantify improvement without a matched
baseline. Raw aggregation saved as perf-summary.json in the run.
Next optimization candidates from frequent top entries: NpcPass/DreamTypeCheck
hooks, ScaledMaxHp and game-tick memory access. Nested timings are not additive;
rare transition spikes are not steady-state cost. No code/build/deploy changes
were made during this investigation.
