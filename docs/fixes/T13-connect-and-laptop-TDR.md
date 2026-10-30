# T13 — join failure and laptop TDR (2026-10-30)

User could not join from laptop; laptop then crashed. Both used T11 DLL and port
f4f0028 with Research=0. Evidence copied to `build/t13/{pc,laptop}.log`.

## Connection failure — Windows UDP port exhaustion on PC

11:57:12 host found user 6283's sign; client received claim, but no native join.
Several attempts continued until 11:59:58, before the driver failure. VPS shadNet
shows RequestSignalingInfos twin -> host and repeated STUN for laptop "host",
but no PC "twin" registration. Relay TCP was connected on both sides.

A full diagnostic PC launch logged `cannot start P2P on UDP port 3658: ENOBUFS`.
Windows UDP bind to port 0 failed WSAENOBUFS (10055); send without explicit bind
failed 10022. Explicit free port 3660 got a valid server STUN reply. `netstat`
listed 16,388 UDP endpoints; 16,308 belonged to MSI.CentralServer.exe PID 8916,
child of MSI_Center_Service PID 5116. Dynamic UDP range is 49152..65535.
Thus signaling discovery over HTTP succeeded while P2P bootstrap could not
allocate its wake socket. This also explains why the old initializer entered the
T12 rollback deadlock; f4f0028 prevents that hang but cannot free other processes'
ports. Earlier T12 description of the temporary socket as wholly redundant was
incomplete: P2P sockets have a transport bootstrap side effect, though native
EnsureTransport retries bootstrap in contexts/ping; this recovered after cleanup.

User authorized MSI Center restart. Elevated script stopped MSI_Center_Service,
closed its leaking CentralServer child and restarted the service. RESTART_OK;
UDP endpoints fell to 85. Bind to port 0 and server STUN reply now succeed.
The already-running diagnostic game recovered automatically; VPS confirms regular
STUN ping from twin on 77.238.225.158:3658 at 12:09:12+ Moscow time.
No firewall/port exclusions/system UDP range changed. No new code deployed.

## Laptop crash — confirmed GPU timeout, cause unresolved

Laptop 12:00:05/07 nvlddmkm event 153; 12:00:06 Display event 4101; WER event 1001
LiveKernelEvent 141 at 12:00:12/25, bucket Turing_SCG3D. Watchdog file:
C:/Windows/LiveKernelReports/WATCHDOG/WATCHDOG-20261030-1200.dmp.
Last laptop mod log 12:00:02, TCP relay left ~12:00:06. upscaler=off,
frame_gen=off. No Application Error 1000 observed in this interval.
This confirms GPU/driver timeout, not a normal mod exception; it does not identify
whether driver, rendering code or other interaction triggered it. Do not claim
Frame Generation is necessary or solved. Full port runtime output is absent from
launcher last_run.log; no graphics settings or drivers changed in this audit.

## Status

Production trace reduction and resolved-banner filter active in logs. Join should
be retested after UDP recovery; an actual new session is not yet confirmed.
TDR unresolved; preserve evidence and correlate next full runtime output before
changing graphics settings. Saves remain untouched in this audit.
