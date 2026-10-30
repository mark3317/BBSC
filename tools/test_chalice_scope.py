"""Exercise production dungeon reads, snapshot assembly and scope switches without a game.

The memory fixture verifies the statically recovered layout, not that the selected altar
is the active guest layout at runtime. That still requires the documented two-PC test.
"""
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "emulator/src/core/bloodborne_re.cpp").read_text(encoding="utf-8")


def function(signature):
    start = SOURCE.index(signature + " {")
    opening = SOURCE.index("{", start)
    depth, end = 1, opening + 1
    while depth:
        depth += (SOURCE[end] == "{") - (SOURCE[end] == "}")
        end += 1
    return SOURCE[start:end] + "\n"


prefix = r'''
#include <algorithm>
#include <array>
#include <cassert>
#include <cstring>
#include <map>
#include <mutex>
#include <optional>
#include <string>
#include <string_view>
#include <unordered_map>
#include <vector>
#define FMT_HEADER_ONLY
#include "fmt/format.h"
#include "core/bbsc_chalice.h"
#include "core/libraries/np/np_signaling/np_signaling_bbsc.h"
using namespace Core::Bloodborne;
#define LOG_INFO(...)
using Packet=Libraries::Np::NpSignaling::SignalingBbscWorldFlags;
u64 image_base=0x100000;
std::unordered_map<u64,u64> memory;
std::array<bool,7> selected{};
std::vector<u8> form(140, 17);
template<class T> T ReadValue(u64 p,size_t off) { return static_cast<T>(memory[p+off]); }
bool ReadablePointer(u64 p,size_t) { return p >= 0x10000; }
bool BbscEventFlag(u32 f) { return f>=9020 && f<=9026 && selected[f-9020]; }
s64 now=1000;
s64 SteadyNowMs() { return now; }
constexpr s64 BbscFollowStaleMs=15000;
bool BbscWarpTogetherEnabled() { return true; }
bool enabled=true;
bool BbscWorldSyncEnabled() { return enabled; }
u32 current=0x1d000000;
u32 GetCurrentPackedMap() { return current; }
bool IsUsablePackedMap(u32 m) { return m && m!=0xffffffff; }
constexpr size_t BbscWorldGroupBytes=125, BbscWorldChunkGroups=8;
constexpr size_t BbscWorldGroupCount=40, BbscDreamGroupCount=57;
constexpr size_t BbscWorldChunkCount=5, BbscDreamChunkCount=8, BbscSnapshotMaxGroups=57;
constexpr s64 BbscWorldFlagsFreshMs=6000;
std::vector<std::vector<u8>> sent;
namespace Libraries::Np::NpSignaling::Helpers {
u32 SendBbscWorldFlagsToPeers(const void* p,u32 size) {
    sent.emplace_back(static_cast<const u8*>(p),static_cast<const u8*>(p)+size); return 1;
}
}
std::array<u8,125> group{};
u64 BbscFlagGroupStorage(u32) { return reinterpret_cast<u64>(group.data()); }
u32 key_of(u32,size_t n) { return static_cast<u32>(12900+n); }
'''

start = SOURCE.index("struct BbscWorldSnapshot {")
end = SOURCE.index("// Host side: one snapshot", start)
snapshots = SOURCE[start:end]
start = SOURCE.index("struct BbscFollowMessage {")
end = SOURCE.index("BbscFollowMessage bbsc_follow_latest{};", start) + len("BbscFollowMessage bbsc_follow_latest{};")
follow = SOURCE[start:end]

scope_prefix = r'''
std::string bbsc_loot_dungeon;
std::map<u32,int> bbsc_loot_groups, bbsc_loot_saved;
std::optional<int> bbsc_loot_slot;
bool bbsc_loot_loaded=false,bbsc_loot_dirty=false;
u32 bbsc_loot_area=0;
bool fail_write=false;
int flushes=0;
void WriteBbscGuestLootFile() { ++flushes; if (!fail_write) bbsc_loot_dirty=false; }
'''

main = r'''
int main() {
    // Seven slots, different altar numbers must resolve identical dungeon data.
    memory[image_base+0x0553e9e8]=0x20000;
    memory[0x20000]=7; memory[0x20008]=0x30000;
    memory[0x30000+2*8]=0x40000; memory[0x40000+0x1d8]=0x50000;
    memory[0x50010]=42;
    memory[0x50058]=reinterpret_cast<u64>(form.data()); memory[0x50060]=form.size();
    selected[2]=true;
    const auto a=ReadBbscChaliceKey(); assert(Chalice::Valid(a));
    assert(a.channel==42 && a.form_size==140);
    OnBbscHostFollowPacket(current,0,0,0,0,1,-1,a);
    selected[2]=false; selected[5]=true; memory[0x30000+5*8]=0x40000;
    assert(ReadBbscChaliceKey()==a);
    selected[1]=true; assert(!Chalice::Valid(ReadBbscChaliceKey())); selected[1]=false;
    memory[0x50060]=2048; assert(!Chalice::Valid(ReadBbscChaliceKey())); memory[0x50060]=140;
    auto unknown=a; unknown.form_version=1; assert(!Chalice::Valid(unknown));
    memory[0x50010]=0x8000000000000000ULL;
    assert(!Chalice::Valid(ReadBbscChaliceKey())); memory[0x50010]=42;
    form[0]^=1; assert(ReadBbscChaliceKey()!=a); form[0]^=1;

    // Actual sender and actual receiver: no publish until all five scoped chunks arrive.
    u64 present=0; group[0]=0x80;
    SendBbscFlagSnapshot(1,current,1,40,key_of,present);
    assert(sent.size()==5 && sent[0].size()==sizeof(Packet)+sizeof(Chalice::Key));
    assert(sent[0].size()+13+8+40 < 1280); // relay envelope, UDP and IPv6 budget
    for (int i=4;i>0;--i) OnBbscWorldFlagsPacket(sent[i].data(),sent[i].size());
    assert(!BbscChaliceLoadReady(current));
    OnBbscWorldFlagsPacket(sent[0].data(),sent[0].size());
    assert(BbscChaliceLoadReady(current));
    BbscWorldSnapshot snap; assert(BbscHostBlockSnapshot(current,snap));
    assert(snap.dungeon==a && snap.groups[0][0]==0x80);
    memory[0x50010]=43; assert(!BbscChaliceLoadReady(current)); memory[0x50010]=42;
    auto switched=a; switched.channel=43;
    OnBbscHostFollowPacket(current,0,0,0,0,2,-1,switched);
    assert(!BbscChaliceLoadReady(current)); // matching old snapshot cannot override new host identity
    OnBbscHostFollowPacket(current,0,0,0,0,3,-1,a);
    current=0x15000000; assert(!BbscChaliceLoadReady(0x1d000000)); current=0x1d000000;
    now=7000; assert(!BbscChaliceLoadReady(current)); now=1000;
    enabled=false; assert(!BbscChaliceLoadReady(current)); enabled=true;

    // Legacy/malformed packets must not publish dungeon state; interleaved identities
    // must not assemble one snapshot from chunks of two different dungeons.
    ClearBbscHostWorldSnapshots();
    auto bad=sent[0]; bad.resize(sizeof(Packet)); bad[5]=1;
    OnBbscWorldFlagsPacket(bad.data(),bad.size()); assert(bbsc_world_blocks.empty());
    bad=sent[0]; bad[17]=0;
    OnBbscWorldFlagsPacket(bad.data(),bad.size()); assert(bbsc_world_blocks.empty());
    bad=sent[0]; bad.push_back(0);
    OnBbscWorldFlagsPacket(bad.data(),bad.size()); assert(bbsc_world_blocks.empty());
    for (int i=0;i<4;++i) OnBbscWorldFlagsPacket(sent[i].data(),sent[i].size());
    bad=sent[4]; Chalice::Key other=a; other.channel=43;
    std::memcpy(bad.data()+sizeof(Packet),&other,sizeof(other));
    OnBbscWorldFlagsPacket(bad.data(),bad.size()); assert(bbsc_world_blocks.empty());
    for (const auto& packet:sent) OnBbscWorldFlagsPacket(packet.data(),packet.size());
    assert(BbscChaliceLoadReady(current));

    // Scope switch flushes first; failed persistence retains the old namespace.
    assert(SelectBbscLootScope(current)); const auto first=bbsc_loot_dungeon;
    assert(first.find("-chalice-")==0);
    bbsc_loot_dirty=true; bbsc_loot_groups[52900]=1;
    fail_write=true; assert(!SelectBbscLootScope(0x18000000));
    assert(bbsc_loot_dungeon==first && bbsc_loot_groups.size()==1);
    fail_write=false; assert(SelectBbscLootScope(0x18000000));
    assert(bbsc_loot_dungeon.empty() && bbsc_loot_groups.empty());
    assert(Chalice::IsLootGroup(52900) && !Chalice::IsLootGroup(52400));
    assert(!Chalice::IsLootGroup(12900));
    sent.clear(); present=0;
    SendBbscFlagSnapshot(1,0x18000000,2,40,key_of,present);
    assert(sent[0].size()==sizeof(Packet) && sent[0][5]==1);
    puts("chalice: native layout, identity mismatch, bounded protocol, chunk isolation, freshness, mounted-entry guard, loot scope/failed persistence PASS");
}
'''

code = prefix + function("Chalice::Key ReadBbscChaliceKey()") + follow + snapshots
code += function("void OnBbscHostFollowPacket(std::uint32_t packed_map, float x, float y, float z, float heading,\n"
                 "                            std::uint32_t sequence, std::int32_t lamp_point,\n"
                 "                            const Chalice::Key& dungeon)")
for signature in (
    "u32 SendBbscFlagSnapshot(u8 version, u32 map, u32 snapshot, size_t count,\n"
    "                         u32 (*key_of)(u32 map, size_t index), u64& present)",
    "bool BbscHostBlockSnapshot(u32 packed_map, BbscWorldSnapshot& out)",
    "bool BbscChaliceLoadReady(u32 map)",
    "void OnBbscWorldFlagsPacket(const void* data, std::uint32_t size)",
):
    code += function(signature)
code += scope_prefix + function("bool SelectBbscLootScope(u32 map)") + main

with tempfile.TemporaryDirectory(prefix="bbsc-chalice-") as tmp:
    cpp, exe = Path(tmp) / "test.cpp", Path(tmp) / "test.exe"
    cpp.write_text(code, encoding="utf-8")
    subprocess.run([os.environ.get("CXX", "g++"), "-std=c++20", "-O2",
                    "-I" + str(ROOT / "emulator/src"),
                    "-I" + str(ROOT / "emulator/externals/fmt/include"),
                    str(cpp), "-o", str(exe)], check=True)
    subprocess.run([str(exe)], check=True, timeout=30)
