from pathlib import Path
import re, subprocess, tempfile
s=Path('emulator/src/core/bloodborne_re.cpp').read_text(encoding='utf-8')
e=re.search(r'const bool host_loaded_there = (.*?);',s,re.S).group(1)
code='''#include <cassert>
struct Host { bool arrival_by_load=true; unsigned arrival_map=24, packed_map=24; long long arrival_ms=100; } host;
long long now=1000, shared_arrival_ms=0;
bool eligible() { return EXPR; }
int main() {
assert(eligible()); shared_arrival_ms=100; assert(!eligible());
host.arrival_ms=200; assert(eligible());
host.arrival_by_load=false; assert(!eligible());
host.arrival_by_load=true; host.arrival_map=25; assert(!eligible());
host.arrival_map=24; now=100000; assert(!eligible());
}
'''.replace('EXPR',e)
with tempfile.TemporaryDirectory() as d:
 p=Path(d); (p/'t.cpp').write_text(code)
 subprocess.run(['g++',str(p/'t.cpp'),'-o',str(p/'t.exe')],check=True)
 subprocess.run([str(p/'t.exe')],check=True)
print('follow arrival: first/new load, consumed load, walking, map and expiry checks PASS')
