#!/bin/sh
# Disassemble the game's code at a BBSC image offset (the same offsets as in bloodborne_re.cpp).
#   tools/eboot-disasm.sh <hex offset> [hex length] [eboot.elf]
# e.g. tools/eboot-disasm.sh 017D89F0 0x400
# The bbport eboot.elf maps code at vaddr 0 from file offset 0x4000 (PT_LOAD 0), so offset X is at
# file byte X + 0x4000. Needs python and binutils objdump (Strawberry Perl ships one on mark-pc).
set -e
off=${1:?hex offset, e.g. 017D89F0}
len=${2:-0x200}
elf=${3:-/d/Games/Bloodborne/bbport-coop/out/eboot.elf}
objdump=${OBJDUMP:-$(command -v objdump || echo /c/Strawberry/c/bin/objdump)}
tmp=$(mktemp)
python -I -c "import sys
f=open(sys.argv[1],'rb'); f.seek(int(sys.argv[2],16)+0x4000)
open(sys.argv[4],'wb').write(f.read(int(sys.argv[3],16)))" "$elf" "$off" "$len" "$tmp"
"$objdump" -D -b binary -m i386:x86-64 -M intel --adjust-vma=0x"$off" "$tmp" | tail -n +8
rm -f "$tmp"
