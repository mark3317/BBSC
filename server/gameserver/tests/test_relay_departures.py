"""Relay EOF notifications must be scoped to the departing player's party."""
import collections
import importlib.util
from pathlib import Path
import struct
import sys
import types
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
spec = importlib.util.spec_from_file_location(
    'bbsc_gameserver', Path(__file__).resolve().parents[1] / 'bbsc_gameserver.py')
server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)


class Peer:
    def __init__(self):
        self.sender_hint = None
        self.session_hint = None
        self.seen_envelope = False
        self.controls = []
        self.frames = []

    def send(self, data):
        self.controls.append(data)
        return 1

    def send_framed(self, data):
        self.frames.append(data)
        return 1


class DepartureTests(unittest.TestCase):
    def setUp(self):
        server.RELAY_CLIENTS.clear()
        server.RELAY_ROSTER = ()
        server.RELAY_HINT_COUNTS = collections.Counter()
        server.RELAY_HINTED_CLIENTS = 0
        # Even when observation and routing are off, departures need party metadata.
        server.ARGS = types.SimpleNamespace(relay_tcp_stats_interval=0,
                                            relay_session_routing=False)

    def join(self, sender, party):
        conn, peer = object(), Peer()
        server._relay_register_client(conn, peer)
        packet = b'SHAD\x40' + struct.pack('<II', sender, party) + b'SHAD\x23'
        server._relay_forward(conn, packet)
        return conn, peer

    def test_guest_eof_notifies_host_and_other_guest_only(self):
        host, hp = self.join(10, 10)
        guest, gp = self.join(11, 10)
        other, op = self.join(12, 10)
        unrelated, up = self.join(20, 20)
        self.assertEqual(server._relay_unregister_client(guest), 3)
        expected = struct.pack('<BII', 0x7E, 11, 10)
        self.assertEqual(hp.controls, [expected])
        self.assertEqual(op.controls, [expected])
        self.assertEqual(gp.controls, [])
        self.assertEqual(up.controls, [])
        self.assertEqual(server.RELAY_HINT_COUNTS, {10: 2, 20: 1})

    def test_host_eof_identifies_host_without_closing_other_connections(self):
        host, hp = self.join(10, 10)
        guest, gp = self.join(11, 10)
        server._relay_unregister_client(host)
        self.assertEqual(gp.controls, [struct.pack('<BII', 0x7E, 10, 10)])
        self.assertIn(guest, server.RELAY_CLIENTS)

    def test_duplicate_eof_does_not_repeat_notification(self):
        host, hp = self.join(10, 10)
        guest, gp = self.join(11, 10)
        server._relay_unregister_client(guest)
        server._relay_unregister_client(guest)
        self.assertEqual(len(hp.controls), 1)

    def test_solo_or_unidentified_socket_cannot_end_a_party(self):
        host, hp = self.join(10, 10)
        solo, sp = self.join(30, 0)
        unknown, peer = object(), Peer()
        server._relay_register_client(unknown, peer)
        server._relay_unregister_client(solo)
        server._relay_unregister_client(unknown)
        self.assertEqual(hp.controls, [])

    def test_changed_party_does_not_notify_previous_party(self):
        host, hp = self.join(10, 10)
        second, sp = self.join(20, 20)
        guest, gp = self.join(11, 10)
        server._relay_forward(guest, b'SHAD\x40' + struct.pack('<II', 11, 20) + b'SHAD\x23')
        server._relay_unregister_client(guest)
        self.assertEqual(hp.controls, [])
        self.assertEqual(sp.controls, [struct.pack('<BII', 0x7E, 11, 20)])


if __name__ == '__main__':
    unittest.main()
