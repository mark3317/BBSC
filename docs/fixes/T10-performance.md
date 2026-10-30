# T10 — game-thread overhead and quiet notifications (2026-10-30)

Requested: reduce cooperative FPS variation, audit obsolete/contradictory guest rules,
keep connection/departure banners, build without deployment. User explicitly chose
only PvP among the additional notices (recovery and deferred rewards go to the log).

## Evidence and changes

Existing laptop profiles in `bloodborne_pc/out/coop-dev/runs/20261030-003555`:
`bbsc-mod-20261030-003739-10040.log` at 00:38:30 reports 4,306 us/frame total,
2,128.5 us/frame in `ChrAction.Flags.Update`, 1,689.6 in the game tick
(`IsValidSos.Update`), and 404.6 in `TickBbscBossLine` (nested, not additive).
These are previous-run observations, NOT a benchmark of this build.

* Production no longer installs diagnostic-only TraceEntry hooks (action flags,
  goods lookups, bell probes, etc.). Functional dispatch, panic, Lua session and
  leave-decision diagnostics stay. Research mode restores the full trace set.
  Functional sites finish before ordinary capture serialization, locking and disk I/O.
  This removes whole register-save trampolines, not merely their log messages.
* Removed the boss-name banner, its lookup and its once-per-second 0x27 packet.
  A complete reference audit found that this packet was UI-only, despite the first
  draft conservatively retaining it. Death/wipe detection uses the local boss bar,
  its death-time latch and life packets, not the banner packet. Receivers accept
  and ignore legacy 0x27 packets; mixed older clients simply lose the named banner.
* Removed the unused 20-second talk-gift rejection heuristic and its 50-entry table.
  SetFlag no longer locks/updates a timestamp map that nobody reads. Actual local
  talk ownership still updates bbsc_action_owner under its existing mutex.
  Removed unused timeout/item constants reported by the compiler.
* Param lookup caches the repository SLOT per type and thread, not a raw table.
  Every hit checks loaded state, follows current holder/resource pointers and
  validates the type name. Changed/unloaded/reused tables fall back to lookup.
* Removed the unused Dream shop guard and its uninstalled hook (the old guard
  reverted the guest's own purchase). The optional legacy host-Dream mode is
  still supported; its working code was not misclassified as dead code.
* Personal map events and door/window knock events share one policy for guest
  permission, local network execution and ownership. Special Byrgenwerth event
  13200055 retains its existing ownership exception. No new quest events enabled.
* Address-only guest condition permissions are cleared when a load creates the
  character, before map events run; a reused address must not inherit permission
  from the previous map. Research-only event/talk logging is now actually opt-in.

## Notifications

Ordinary BBSC notices are log-only. Keep PvP on/off/alone and lost-host departure.
Modified co-op message IDs for search/death/boss/follow/arrival receive an ASCII
sentinel; the banner menu hook clears the pending bit before drawing it, avoiding
an empty banner. Actual connection/departure lines, vanilla item popups, item names,
menus and interactive bell confirmations remain. The blanket 8-second join quiet
window was removed because it also hid the actual connection notification.
Unknown `?ActionEventInfo?` banners are suppressed at the same display boundary.
Generated English/Russian tables remain source data; one ID policy covers both.

## Validation and limits

`python tools/test_perf_policy.py`: PASS. Runs extracted C++ helpers against fake
memory: warm-cache cost, unloaded params, changed table, changed repository/slot,
wrong type and invalid pointer; checks notification policy and coverage of every
functional dispatch offset by the production hook selector.
`git diff --check`: PASS.
Build result will be recorded after compilation.

No game launch, deployment, save changes, server changes or push authorized/performed.
A later same-scene host/guest profile is needed to measure actual FPS improvement.
Core hooks that call engine functions remain on the game thread: moving them to a
worker would race map loads, event processing, inventory and death transitions.
Durable journals still flush synchronously at critical transitions; this patch does
not weaken recovery guarantees to hide disk latency. Legacy optional Dream mode,
NPC ownership guards and item recovery are not removed without proving redundancy.
