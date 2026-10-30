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

## Control with both DLSS features OFF — 16:35–16:36 Moscow

User reports crash on first travel to Hunter's Dream. PC ini mtime 16:35:24,
process 43796 starts 16:35:36: upscaler=off AND frame_gen=off confirmed and copied.
The game initially loads Cathedral Ward, session state 0/solo at 16:36:09, then
OwnWorldStep/SkippedCleanup at 16:36:22.548–.564; no completed Dream arrival is
logged. Windows again records nvlddmkm 153 at 16:36:22 and 16:36:26, WER
LiveKernelEvent 141 at 16:36:33, report facbbd68-2f57-4d89-911c-8e325810f370,
WATCHDOG-20261030-1636.dmp referenced. Captured separately in run
`20261030-163400-no-dlss` (PC logs and Windows events).

This reproduces the GPU TDR with both DLSS features disabled and no active co-op
session. Neither feature nor an active peer is a necessary condition. BBSC is
still injected in this run; solo is not a no-mod control. Next discriminating
control is the same port/config/character in launcher Offline mode without BBSC,
then travel to Dream and return/title transitions. Do not attribute the fault to
GPU hardware, NVIDIA alone or a particular BBSC hook from timing correlation.
No settings, saves, binaries or driver changed during collection.

## Offline/no-BBSC control — 16:37–16:39 Moscow

User reports same Dream-travel crash in launcher Offline mode. Saved play_mode is
`offline`, latest last_run.log starts 16:37:59, no new BBSC logs/captures were
created after the previous 16:35:36 process. Launcher playSelected routes Offline
to normal play(), not coopPlay(). Both DLSS settings remain OFF. This is strong
control evidence that BBSC injection is not required; no live module snapshot was
possible after process exit. Other game mods remain: pc-menu and Xbox prompts.

New GPU errors: nvlddmkm 153 at 16:39:04 and 16:39:09. New WER 141 at 16:39:13,
report 1efae228-6e54-4c83-a894-b0e740685d95, WATCHDOG-20261030-1639.dmp.
The 16:39:19 archive entry instead belongs to the PREVIOUS 16:36 incident; do not
count it as another crash. Collected as `20261030-163700-offline`.

Next isolation target is shared renderer/driver path, not T17 queue logic.
Driver 621.01 still installed. Controlled driver replacement/rollback followed by
same Offline Dream route is appropriate; not performed automatically. No evidence
yet distinguishes driver, port resource lifetime/synchronization, other game mods
or hardware instability. WATCHDOG folder access denied in current process;
dumps not analyzed. No binary/settings/save changes during this investigation.

## Clean reinstall of the user's own build — 16:50 Moscow

User correction: do not install/update upstream releases; use own build as on
laptop. Independent launcher fork is future intent. Downloaded upstream v2.3.2
was not installed. Source: own T16 ZIP, saved SHA256/CRC verified. Compared 5102
runtime files to laptop: 5098 match; copied exact laptop Bloodborne.exe,
bin/bb-probe.exe, _internal/base_library.zip and Discord Rich Presence exe for the
four differences. All runtime hashes checked before directory swap; four copied
binary hashes checked again after. Current T17 BBSC override preserved.

New install at D:/Games/Bloodborne/bbport-coop. Old folder renamed to
D:/Games/Bloodborne/bbport-coop.before-clean-20261030-164954. Migrated 16 files
including game/input/mod/server configs, prompt mods, custom config and BBSC.
APPDATA settings unchanged; 16 save hashes unchanged in external testHost.
No game files touched. Old generated out/internal caches not migrated. External
user_dir (including its caches) unchanged. Games/launchers stopped during swap.
Manifests/result in D:/Games/Bloodborne/coop-dev/clean-own-T17-20261030/.
No driver, auto-update settings or source changes. Game not launched.
Next control: Offline Dream travel, upscaler=off/frame_gen=off.

## First post-reinstall success and out comparison

User reports Dream loading no longer crashes after reinstall. No driver update.
Compared old/new out: boot.bin, eboot.elf, boot-libc.bin, boot-linked.bin,
entry.bin, analysis/link/libc-link JSON and content/profile files are identical.
All 9907 shader_code data files identical; only stamp.txt timestamps differ
(9908 total files). All 26 enhancement files match, scripts/_internal/bin match
apart from two old bb-probe backup files absent in clean install.

patches.bin has 248 old vs 247 new records: sole difference is old offset
0x1b39030, Skip Online/Offline Choice. This is expected from old Offline vs new
Coop mode (current setting coop, new BBSC process 2092 at 16:51:55). Not evidence
of corrupt patch data. GPU cache is under external BB_GPU_USER_DIR=testHost,
which was preserved; out/shader_code is extracted input, not the driver pipeline
cache. Cannot claim corrupted shader bytes or a proven fix from this one success.
Generated state, timing, old transient mod views and stochastic failure remain
possible. Preserve old installation for controlled comparison; no live cache
changes while game runs. Recommend repeated same-mode Dream/return transitions
and Offline comparison before attributing cause to out.
