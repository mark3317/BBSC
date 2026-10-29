"""T5 (2026-10-29): who starts each talk-driven event (BbscTalkEventTriggers in bloodborne_re.cpp).

    python -I talk_event_owners.py [cpp]     a report: per event, its player-action conditions
                                             (action button, boss door, dialog choice), where its
                                             first SetEventFlag stands (before any condition =
                                             the event's own reset), and the C++ list of action events

An event that waits on a player-action condition (bank 3: 5 action button, 13 boss-room action
button, 18/19 the same with a direction, 24 action button in an area, 27 dialog branch) is started
by the player who pressed: its condition passes only in that player's game, so the run is that
player's own (the knock on a window, a lever, a door with a talk). Names from common.emedf.
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bbfiles  # noqa: E402
import emevd  # noqa: E402

bbfiles.GAME = os.environ.get('BB_GAME', r'D:\Games\Bloodborne\game\dvdroot_ps4')
ACTION = {5: 'action button', 13: 'boss-room action button', 18: 'action button (direction)',
          19: 'boss-room action button (direction)', 24: 'action button in area', 27: 'dialog branch'}
CONDITION_BANKS = {0, 1, 3, 4, 5, 11, 1000, 1001}


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    cpp = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, '..', '..', 'emulator', 'src',
                                                                 'core', 'bloodborne_re.cpp')
    src = open(cpp, encoding='utf-8').read()
    block = src[src.index('BbscTalkEventTriggers{{'):]
    block = block[:block.index('}};')]
    pairs = [(int(a), int(b)) for a, b in re.findall(r'\{(\d+), (\d+)\}', block)]
    events = {}
    for e, f in pairs:
        events.setdefault(e, []).append(f)
    folder = os.path.join(bbfiles.GAME, 'event')
    found = {}
    for name in sorted(os.listdir(folder)):
        if not name.endswith('.emevd.dcx'):
            continue
        for eid, instrs in emevd.Emevd(os.path.join(folder, name)).events:
            if eid in events and eid not in found:
                found[eid] = (name.split('.')[0], instrs)
    action_events = []
    print(f'{len(events)} talk-driven events, {len(pairs)} (event, flag) pairs; found in the files: '
          f'{len(found)}')
    print('event     file          action conditions                     first SetFlag  triggers')
    for eid in sorted(events):
        if eid not in found:
            print(f'{eid:<9} (not in any event file)')
            continue
        name, instrs = found[eid]
        actions = sorted({ACTION[i] for b, i, _ in instrs if b == 3 and i in ACTION})
        first_cond = next((k for k, (b, i, _) in enumerate(instrs) if b in CONDITION_BANKS), None)
        first_set = next((k for k, (b, i, _) in enumerate(instrs) if b == 2003 and i in (2, 22)),
                         None)
        if first_set is None:
            where = '-'
        elif first_cond is None or first_set < first_cond:
            where = f'#{first_set} reset'
        else:
            where = f'#{first_set} after'
        if actions:
            action_events.append(eid)
        print(f'{eid:<9} {name:<13} {", ".join(actions) or "-":<37} {where:<14} '
              f'{" ".join(map(str, events[eid]))}')
    print(f'\n{len(action_events)} event(s) started by a player action:')
    print(', '.join(map(str, action_events)))


if __name__ == '__main__':
    main()
