# T12 — PC cooperative startup hang (2026-10-30)

User: game no longer starts on PC. T11 DLL installs correctly, production trace
selection 31/31 (137 omitted) confirmed. Local startup evidence is in
`BBSC/build/startup-*.log` and `online-nomod-stacks.txt` (not committed).

Exact online launch, including SHADNET credentials, hangs at a grey window before
the title screen. Reproduced with and without the BBSC DLL. Offline/no-account
comparison reaches title menu. LLDB no-mod stack:
main -> sceNpSignalingInitialize -> StopDispatchThread -> sceNpJoinThread;
dispatch -> ProcessPendingActivations -> SignalingMutexGuard -> mutex lock.
The initializer owns that same mutex while rolling back failed startup, so joining
the dispatch thread deadlocks. StartEchoRuntime opens a temporary type-6 socket
only for an ioctl that bbport already stubs as ORBIS_OK; socket creation can fail
and unnecessarily initiate rollback.

Port commit f4f0028 removes the pointless socket and releases initialization's
signaling guard before starting worker threads. Error logs added for echo/callout
startup failures. This is a port/bbnet fix; BBSC DLL remains T11 (8373921).

Validation: `python tools/test_signaling_startup.py` PASS; runs the actual extracted
startup functions with a real worker contending for the signaling mutex, covers
success and rollback after echo/callout failures with a timeout. `bash build.sh`
succeeded. Updated only PC install bin/bb-probe.exe, SHA256:
FB99FE9DAEF0DE8F8DE9973D003B734B3ABAF6FBEC44A13DF38604B48B5E98DE.
Backup: bin/bb-probe.exe.bak-signaling-20261030-115000.
Full cooperative launch with T11 DLL + Research=0 now creates SceNpSignalingCallout
and reaches the title menu, confirmed visually at 60 FPS. Game left at title;
no world loaded or save restored in this diagnosis. Laptop runtime not changed.
Saves remain forest-host on both machines as copied earlier. Multiplayer gameplay
and startup error handling on an actual failed network remain separate checks.
