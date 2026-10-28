# Область 1 — устройство игры (GI)

Цель: CUSA03173 v1.09 (eboot, sha256 d65f0b4f…), все адреса — смещения от `image_base`. Источник —
`emulator/src/core/bloodborne_re.cpp` (`re:`), `bbsc_patch_tables.h` (`pt:`), `tools/gamedata`. Event-флаги, Сон,
предметы для синхронизации подробно — в `bbsc-world-sync.md`; транспорт — в `bbsc-session-network.md`.

## 0. Проверка адресов (2026-10-29)
Скрипт прошлого агента (scratch `gi/verify.py`) сверил с `D:\Games\Bloodborne\bbport-coop\out\eboot.elf`
(файл = VA + 0x4000): **57/57 записей таблиц патчей** (retarget call/jmp, edit-байты, entry) и **168/168 trace/hook-сайтов**
(ожидаемые прологи) — все совпали. Не проверены этим скриптом: 94 прямых вызова функций по смещению
(`reinterpret_cast<…>(image_base + 0x…)`) и глобальные указатели данных.

## 1. Глобальные указатели (`[image+X]`)
| Смещение | Что | Где |
|---|---|---|
| 0x05556678 | GlobalState (сессия/загрузки/варпы) | `re:131` |
| 0x05540290 | MultiPlay/matching state; `+0x124` = **состояние сессии** (3/4/6) | `re:135`, `re:4155-4158` |
| 0x0553E878 | WorldChrMan: `+0x60` локальный PlayerIns, `+0x30/+0x38` список персонажей (шаг 0x38) | `re:132`, `re:4277-4290` |
| 0x0553B130 | PlayerSlotMan / GameData: `+0x08` локальный слот, `+0xA4` тип игрока (1 кооп, 2 инвейдер); `+0x8`→player game data (`+0x1D0` инвентарь для AddItem, `+0x328` для поиска) | `re:3512`, `re:3533-3540`, `re:18164-18174` |
| 0x0553B100 | SprjEventFlagMan (флаги) | `re:5187-5205` |
| 0x0553B108 / 0x0553B0C8 | SprjEventMan / SprjLuaEventMan | `re:8395`, `re:1567` |
| 0x0553B120 / 0x0553D6D0 / 0x0553D750 / 0x0556E560 | SummonManager root / правила сессии призыва / таблица ролей (34×0x80) / роли сборки призыва | `re:133-140` |
| 0x0553B148 | Список текущих карт: `+0x10` массив (`+0x18` count, `+0x20` ptr, шаг 0xA0, `+0x08` packed map), `+0x20` индекс текущей | `re:1223-1240`, `re:4856-4880` |
| 0x0553D6E0 | ItemMan | `re:10634` |
| 0x05540230 | MultiPlayMan | `re:3513` |
| 0x05540300 / 0x05540340 | MsgRepository (FMG) / SoloParamRepository | `re:13820`, `re:10333` |
| 0x05562878 | Boss gauge (до 3 боссов, `+0x1658+i*0x14`) | `re:4175`, `re:4163-4170` |
| 0x05540068, 0x05581410/0x055813D8/0x055813E0, 0x056C7048 | Fade, баннер (текст/флаг), online state | `re:7233`, `re:14097`, `re:204` |

**Поля GlobalState** (самые частые): `+0x08` u8 идёт загрузка (39 чтений) · `+0x1592` u8 «свой мир» (34) ·
`+0x14C4` карта назначения summon-reload (phase 3) · `+0x14F0` карта загрузки, `+0x1500/+0x1510` точка «домой» ·
`+0x1520` «игнорировать последнюю лампу» · `+0x1522/+0x1523` смерть/падение · `+0x1528` event point последней лампы ·
`+0x1690..+0x16D8` состояние смерти/эхо · `+0x16F0` тип знака призыва · `+0x16F8` → transition (`+0x08` кооператоры,
`+0x18` число участников, `+0x98`) · `+0x1770`.

## 2. Скрипты игры и точки входа
- **EMEVD** (события карт): bank 2003 handler 0x017C0420 (RSI = экземпляр события) — хук «talk-driven events»; 2005 объекты 0x017C46E0, 2006 SFX 0x017C64E0; шаг события 0x012ECDC0; выдача лота 2003[04] → AwardItemLot 0x017DDC50 (`re:10093-10099`, `re:10635`, `re:12952`). Читалка `tools/gamedata/emevd.py` (64-bit EVD).
- **Флаги**: SetFlag 0x013CFCC0 (лист, хук всех установок), чтение 0x013CFD80 / GetEventFlag 0x01399BF0, обёртка SetEventFlag 0x0132E5A0 (её зовёт BBSC); конструктор менеджера 0x013CF0E0 (`re:5187-5188`, `re:10328`, `re:13031-13040`).
- **ESD (разговоры)**: шаг разговоров 0x0204C6D9 → state machine 0x02044C80; диспетчер команд 0x0203FFD0 (c1_11 SetFlag, возврат 0x02043F5C); c1_65 окно «получен предмет» 0x020436E4; vtable условий 0x0535AAB0 (`re:12596-12656`, `re:12700`, `re:10326`). Читалки `esd.py`, `esd_dump.py`.
- **Lua** (скомпилированный Lua 5.0, `script/*.luabnd.dcx`, `lua50.py`): BlockClear2_1/_3Leave/_3 0x01385470/0x013858A0/0x01385930, SoloPlayDeath_2 0x01381DE0, PartyGhostDeath_2 0x013824C0, Failed_BossAreaMission 0x0138B2D0, RegistReturnTitle 0x0138B990 / Check 0x0138BAD0 / On 0x0138BAF0 (`re:3950-3951`, `re:4226`, `re:8919-8921`, `re:9115-9122`).
- **Предметы**: AddItem 0x014CDFD0(inv=player+0x1D0, type, id, count,1,1,0), поиск в инвентаре 0x014D9E80(player+0x328, type, id), очередь попапов 0x016D8850; подбор 0x017D8570 / выдача лота 0x017D89F0 / включение предмета 0x017D9E70; строка ItemLotParam 0x94 байта; goods = type 0x40000000 (`re:12699`, `re:13194-13196`, `re:13381`, `re:10993`, `re:18145-18151`).
- **Параметры**: NpcParam row 0x01F226C0 (`+0x145` флаги, бит 0x80 «бродячий призрак»), ShopLineupParam (qwcId/eventFlag), kill reward 0x018C5070/0x018FC860/0x018FC1E0 (`re:10332-10335`, `re:14415-14417`). Читалка `param.py`.
- **Катсцены**: 6 вариантов запроса 0x0131A9F0…0x0131C170 (`re:18029`).
- **Карты**: packed map `0xAABB0000` (AA область, BB блок); 21 = Сон охотника (0x15000000), 29 = чаши (id карт общие для всех подземелий). MSB читает `msb.py`, туманные стены — `find-fog-walls.py` (CalcGetMultiWallEntityId 0x01338840), `fog_survey.py`, `chalice_walls.py`.

## 3. Патчи сохранения сессии (`pt:`)
Группы `pt:31-47`: Stage(10), Revive(4), Boss(4), MatchCheck(4), Lamp(6), Tasks(3), HostDead(6), NoFogWalls(2), LeaveLimit(2),
Spectate(3), Echoes(4), GuestItems(22), SolidNpcs(2), Scaling(3), KitBells(2), SendBacklog(2). По заметкам sn/: Boss/LeaveLimit по
умолчанию выкл., Stage/Revive всегда, MatchCheck/Tasks/HostDead/Spectate по умолчанию вкл.

## 4. Сейвы
- Сейв игры: `…\savedata\CUSA00207\SPRJ0005\userdata0000..0009` (save id CUSA00207 ≠ title id CUSA03173). Пользователь `1004` никогда не трогается (`re:6236-6238`).
- «Активный слот» = самый новый по mtime `userdataNNNN`, **записанный после старта этого запуска** (`re:6202-6270`); база — `<cwd>\user` или `%APPDATA%\shadPS4`, плюс `BBSC_SAVE_DIR` (ставит лаунчер `bloodborne_pc/launcher/bbport_coop.py:732-740`).
- Файлы BBSC рядом с captures: `own-world/`, `shared-progress/`, `guest-items/`, `save-backups/before-duel-bell-<ts>/` (`re:6296`, `re:11500`, `re:15612-15680`).

## 5. Выгрузки `BBSC/build/*.txt`
`npcflags.txt` (= BbscNpcQuestFlags), `pairs.txt`/`indiv_pairs.txt` (event→flag, источник BbscTalkEventTriggers), `evids.txt`, `sync_events.txt` (события и kind флагов), `indiv_events.txt` (пустой).

## Кандидаты в находки
- **GI-1 Прямые вызовы функций игры без проверки пролога.** Сайты хуков проверяются по байтам при установке (168/168 ОК), но
  ~94 функции вызываются по голому смещению (0x0132E5A0, 0x014CDFD0, 0x017DDC50, 0x014D9E80, запрос катсцен…). На другом eboot
  (не 1.09 или пропатченном) — вызов в произвольный код. Проверить, есть ли общий гейт версии до этих вызовов. Низкий для своей сборки.
- **GI-2 Слот сейва неизвестен до первого сохранения в этом запуске** (`re:6216-6218`: `best_time = bbsc_run_started`). До первого
  автосейва `BbscActiveSaveSlot()` пуст → own-world и pending progress пишутся только в память (`re:6454-6457`). Краш гостем до
  первого сейва запуска = потеря собственного мира на диске. Плюс, без `BBSC_SAVE_DIR` в bbport поиск идёт в путях shadPS4 — проверить
  в области 5, всегда ли лаунчер его ставит (тест `test_coop.py:86`: без сейвов переменная не ставится).
  → Проверено в области 5: лаунчер ставит `BBSC_SAVE_DIR` на **копию** сейвов, см. **LA-1** (`launcher.md`).
- **GI-3 Бэкапы сейвов не чистятся.** `BackupBbscSavesUnchecked` копирует все папки CUSA00207 в новую `save-backups/before-duel-bell-<ts>`
  при каждой выдаче колокола и перед каждым слиянием прогресса (`re:11419-11421`); удаления старых не видно (`re:15630-15690`). Имя
  папки вводит в заблуждение для бэкапов прогресса.
- **GI-4 Чтение `global+0x1528` как s64** (`re:13648`) при s32-поле лампы (`re:4825`, другие чтения s32): захватывает и `+0x152C` —
  трассировка сработает на изменения соседнего поля. Только диагностика, низкий.
- **GI-5 Магические числа без имён в сетевом/игровом коде**, напр. `0x0553B0D8` (`re:11732`, `re:12795`) и `0x0553B130` повторно
  как литерал (`re:12748`, `re:18165`) рядом с именованным `PlayerSlotManagerPointerOffset` — риск рассинхрона при правке. Стиль, низкий.
