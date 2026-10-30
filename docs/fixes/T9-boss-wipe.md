# T9: delayed client death bypassed the boss wipe reload

## Evidence (30 October 2026, local time)

Run `20261030-003555`, PC log `bbsc-mod-20261030-005235-48728.log`,
laptop log `bbsc-mod-20261030-005315-9304.log`.

- 01:06:05 host died at Shadows of Yharnam; 01:06:56 client died.
- 01:06:58 host requested its normal wipe reload; 01:07:03 host alive after load.
- 01:07:11 client watchdog reached 15 seconds, directly requested the death curtain.
- 01:07:12 client revived IN PLACE at the host lamp (-190.12, -76.29, 252.22).
- 01:07:13 native PartyGhostDeath_2 finally arrived, 1763 ms after that revival,
  and was skipped as a late death step. The client never reloaded the boss map.
- A later client process still showed the Shadows boss bar, matching the user report.

The watchdog had boss handling only for repeat deaths, and even that branch did not
initialize the full wipe-follow state. The normal delayed death branch revived directly.
The 10-second boss-bar memory also expired before the 15-second watchdog / 17-second
native death step. A character pointer change was incorrectly accepted as a completed load.

## Change

1. Latch boss context at HP zero / Failed_BossAreaMission, retain it for this death.
2. Route ALL watchdog deaths through the same BeginBbscCoopDeath state machine as
   the native step, including solo/invasion handling, host-revival epoch and wipe follow.
   Preserve the echoes snapshot recorded at HP zero for repeat deaths.
3. A late native step does not restart a death already owned by the watchdog.
4. Require the actual completed-load generation before reviving a spectating player;
   ignore watchdog time spent loading. No pointer-based proof of a load remains.
5. Clear all three native HUD boss slots and cached boss context after the death load
   and after confirmed session exit/recovery at home. No defeat flags or rewards change.

Applies to all bosses, including multi-bar bosses and chalice encounters, without boss IDs.
No protocol/server changes. The forest-host snapshot must never be overwritten.

## Validation

Build and deployment results recorded below. Gameplay validation is still required.

Test as PC host / laptop client, current test saves (no automatic rollback):
1. Enter Shadows together; host dies first, client waits at least 20 seconds, then dies.
   Both should reload at the host lamp; no boss bars at the lamp, session remains usable.
2. Enter again; client dies first, host then dies. Same result.
3. Exit the session: no boss bars at home, lamp works. Rejoin and enter the fight again.
4. If practical, one death outside a boss fight with a living partner should still revive
   without loading; a boss killed while a partner is spectating should still revive it.

Separate audit lead: Shared Progress OR-merges kind-1 flags, which may retain transient
encounter flags such as 12704800/12704801. This is not proven as the cause in this run;
no broad event-flag changes are bundled with this confirmed death-state fix.


Build/deploy: code commit `12984a9`, build log `exit=0`, 8 existing unused-symbol warnings.
PC and laptop override + active-package DLL hashes verified:
`68943CD98A535BCEB9771F5B5DB9FCFC3DD696EDA50747D5ABECD1DE23F514AF`.
Native ClearBossGauge disassembled at 0x01336D00: only resets HUD slots, no calls/flags.
Current testHost/test saves kept. No save rollback, no server changes.
