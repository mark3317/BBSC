# T15 — join loading UI and NPC solidity

Removed BBSC pre-opening of the logo-only NowLoading menu and forced MenuMan+0x808=2.
StageFlow chooses the native loading UI. Existing fade covers placement between transitions;
this does not eliminate the underlying native two-stage summon/cross-map transition.

Solid NPC worker previously exited after its first successful NpcParam pass. It now reapplies
wander-ghost flags to all discovered copies after each completed load. Scanning stays off the
main thread and is skipped while the applied load generation is unchanged. New copies may
remain unpatched until the asynchronous scan finishes; visual absence of all transient ghosts
has not been established. Existing creation patch remains enabled.

Code d13754c. Existing perf/policy and all 15 post-load fixtures pass. These do not test visual
rendering. In-game confirmation required for same-map/cross-map joins and NPCs across reloads.
No deployment or save modifications in this turn.
