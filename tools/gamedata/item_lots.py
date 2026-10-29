"""Items, item lots and their get flags (the questions of docs/fixes/K2-items.md).

    python -I item_lots.py name <text>        goods / runes whose Russian or English name has <text>
    python -I item_lots.py goods <id>...      a goods row: type, isGuestDrop, isOnlyOne, maxNum, names
    python -I item_lots.py lot <lot>...       a lot's entries (category, id, count, weight, flags)
    python -I item_lots.py flag <flag>...     the lots whose get flag is <flag>
    python -I item_lots.py keylots            every lot giving a key item (goodsType 1) and its flag

Categories in ItemLotParam: 0 weapon, 1 attire, 2 accessory, 4 goods, 8 blood gem / rune (the id is
a GemGenParam row), 15 other. Rune names are in menu.msgbnd 魔石名.fmg, goods names in item.msgbnd.
GAME defaults to D:\\Games\\Bloodborne\\game\\dvdroot_ps4 (set BB_GAME to override).
"""
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bbfiles  # noqa: E402

bbfiles.GAME = os.environ.get('BB_GAME', r'D:\Games\Bloodborne\game\dvdroot_ps4')
import param  # noqa: E402


def fmg(bnd, lang, name):
    files = bbfiles.read_bnd4(bbfiles.read_dcx(os.path.join(bbfiles.GAME, 'msg', lang, bnd)))
    return bbfiles.read_fmg(files[name][1])


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd, args = sys.argv[1], sys.argv[2:]
    ru = fmg('item.msgbnd.dcx', 'rusru', 'アイテム名.fmg')
    en = fmg('item.msgbnd.dcx', 'engus', 'アイテム名.fmg')
    gems_ru = fmg('menu.msgbnd.dcx', 'rusru', '魔石名.fmg')
    gems_en = fmg('menu.msgbnd.dcx', 'engus', '魔石名.fmg')
    glay, _, gdata, grows = param.load('EquipParamGoods')
    llay, _, ldata, lrows = param.load('ItemLotParam')

    def goods(i):
        return param.row_values(glay, gdata, grows[i]) if i in grows else None

    def lot_entries(lot):
        v = param.row_values(llay, ldata, lrows[lot])
        out = []
        for k in range(1, 9):
            item = v[f'lotItemId0{k}']
            if item > 0:
                out.append((v[f'lotItemCategory0{k}'], item, v[f'lotItemNum0{k}'],
                            v[f'lotItemBasePoint0{k}'], v[f'getItemFlagId0{k}']))
        return v['getItemFlagId'], out

    if cmd == 'name':
        text = ' '.join(args).lower()
        for table, names, other in ((ru, en, 'goods'), (gems_ru, gems_en, 'gem name')):
            for k, v in sorted(table.items()):
                if v and (text in v.lower() or text in (names.get(k) or '').lower()):
                    print(other, k, v, '|', names.get(k))
    elif cmd == 'goods':
        for i in map(int, args):
            g = goods(i)
            if g is None:
                print(i, 'no row')
                continue
            print(i, ru.get(i), '|', en.get(i), {k: g[k] for k in (
                'goodsType', 'isGuestDrop', 'isOnlyOne', 'maxNum', 'isConsume', 'enable_white')})
    elif cmd == 'lot':
        for lot in map(int, args):
            flag, entries = lot_entries(lot)
            print(lot, 'lot flag', flag)
            for cat, item, num, weight, eflag in entries:
                name = ru.get(item) if cat == 4 else ''
                print('   cat', cat, 'id', item, 'x', num, 'weight', weight, 'flag', eflag, name)
    elif cmd == 'flag':
        wanted = set(map(int, args))
        for lot in sorted(lrows):
            flag, entries = lot_entries(lot)
            if flag in wanted or any(e[4] in wanted for e in entries):
                print(lot, 'lot flag', flag, entries)
    elif cmd == 'keylots':
        for lot in sorted(lrows):
            flag, entries = lot_entries(lot)
            for cat, item, num, weight, eflag in entries:
                g = goods(item) if cat == 4 else None
                if g and g['goodsType'] == 1:
                    print(lot, item, ru.get(item), '| flag', eflag or flag)
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
