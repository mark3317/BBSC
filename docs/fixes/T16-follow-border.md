# T16 — repeated border loads

Latest logs copied to build/t16/{pc,laptop}.log. Guest repeatedly requested follow warp
from 0x18010000 to 0x18000000 at 14:00/14:01, attempts 1..3, reason host arrived by a load.
The arrival marker remained eligible for 90 seconds even after the guest reached the host.
Track the host arrival timestamp last shared by both players; only a newer host load can
force a same-area follow. No world/progress/save writes added. New session clears the marker.

Host stopped shortly after 14:02:03. Windows WER at 14:02:12/41 records LiveKernelEvent 141,
nvlddmkm.sys Blackwell, WATCHDOG-20261030-1402.dmp. Driver/GPU hang confirmed; causality
from co-op/progress mismatch not established. Do not claim this code fixes TDR.

Test in game: join an advanced host, cross Cathedral Ward/Central Yharnam border repeatedly,
then host travels by lamp: guest should still follow the new load. Saves remain untouched.
