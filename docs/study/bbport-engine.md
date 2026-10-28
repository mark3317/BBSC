# Область 4 — порт bbport и подключение мода (PE)

Ссылки: `probe:` = `bloodborne_pc/src/probe.c` (815), `eh:` = `src/engine_hooks.c`, `mod:` = `BBSC/emulator/mod/bbsc_mod.cpp`,
`hooks:` = `BBSC/emulator/mod/bbsc_hooks.cpp`, `launch:` = `BBSC/emulator/mod/bbsc_launch.cpp`, `patch:` = `BBSC/bbport/bbport-1.7.2-bbsc.patch`.
Не читались подробно: `pc_menu.c`, `rebirth.c`, `runtime_*.c`, `aspect_ratio.cpp`, `gpu/` (видеоядро), bbnet целиком.

## 1. Цепочка запуска (кооп)
1. Лаунчер ставит `BB_PROBE=bbsc-launch.exe`, `BBSC_EMULATOR=<bb-probe.exe>`, `BB_COOP=1` (см. `launcher.md`); run.py вызывает «probe».
2. `bbsc-launch.exe` (`launch:1-20`, bbport-ветка `launch:264-360`): запускает `bb-probe.exe` **приостановленным**, удалённым
   `LoadLibraryW` (VirtualAllocEx + поток) грузит `bbsc.dll`, затем отпускает процесс; вывод — в `user\last_run.log`.
3. `bb-probe.exe` (`probe.c`): загружает ELF игры, применяет `patches.bin` (245 записей) и свои патчи — задержка респауна 12 с → 0
   (`BB_RESPAWN_DELAY_FIX`, `respawn_patch.h`), куча меню +8 МБ (`menu_heap_patch.h`), map/confirm guards, атлас/карта, выносливость,
   engine hooks (pc_menu, key prompts, mouse camera, occlusion, aspect…). Все сайты проверяются длиной + FNV-1a хешем (`code_check.h`).
   При `BB_COOP=1` код игры остаётся **RWX** для хуков BBSC (`probe:764-771`), иначе RX.
4. `bbsc.dll` (`mod:1-20`, `mod:375-420`): ждёт образ (`FindEbootBase` `mod:227-260`: сначала адрес форка shadp2p, иначе скан
   VirtualQuery по исполняемым регионам с проверкой 4 сайтов), снимает защиту кода (RWX), проверяет ВСЕ сайты патчей до записи,
   пишет `bbsc_patch_tables.h`, ставит хуки (`hooks:` — трамплин со снимком всех регистров + YMM), дальше следит и переписывает
   сайты, которые «откатил» хост. Обёртка чтения геймпада через слот импорта `mod:864-880` (F1-камера по L3+R3).

## 2. Трамплины и пересечения
- BBSC: последний 1 МБ 8-МБ RWX-области эмулятора после образа (если она есть и вся нулевая), иначе свой 1 МБ RWX за
  `image + 0x056D4000 + 8 МБ` или перед образом, в пределах rel32 (`hooks:38-95`).
- Порт: свои заглушки 64 КБ (`eh:14`, `eh:42-71`) сразу за образом, заполнены `0xCC` → проверка BBSC «всё нули» их не захватит. Конфликта нет.
- Скрипт прошлого агента `pe/overlap.py` (запущен 2026-10-29, только чтение): **275 сайтов BBSC против 299 сайтов порта (вкл. 245 записей
  `bbport-coop\out\patches.bin`) — 0 пересечений** (с запасом ±8 байт). Адреса сайтов порта в скрипте вписаны вручную.

## 3. Сеть порта (bbnet) и патч BBSC
- `patch:` меняет: `np_matching2_signaling.cpp` (693+), `np_signaling_helpers.cpp` (513+), `p2p_sockets.cpp` (455+), `np_signaling_state.*`,
  `np_utility` (sceNpLookupNpId онлайн — нужно для 3-го игрока), `np_signaling_bbsc.h` (типы SHAD-пакетов), `bbnet_glue.cpp`.
- В форке `bloodborne_pc` эти файлы живут уже в `gpu/bbnet/vendor/shadps4/core/...` (+ `bbsc_relay_client.h`, `bbsc_fast_sign.*`, `net/p2p_relay.cpp`),
  последние правки: `1c9a2ea` (Offer от неизвестного пира), `0a5167e`, `9627500`.

## Кандидаты в находки
- **PE-1 Патч `bbport-1.7.2-bbsc.patch` устарел.** Пути `gpu/shadps4/...` не совпадают с форком (`gpu/bbnet/vendor/shadps4/...`), а
  содержимое отстаёт: в форковом `np_signaling_bbsc.h` есть `kSignalingBbscPvpType = 0x25` и `SignalingBbscPvp`, в патче нет (diff 2026-10-29).
  Два источника правды для протокола; CLAUDE.md BBSC указывает на патч как на актуальный.
- **PE-2 Код игры RWX весь запуск коопа** (`probe:764-771` и повторно `mod:394-416`): нет W^X, любая порча указателя может переписать
  код. Нужно BBSC (прямая запись байтов). Низкий для безопасности, но усложняет отладку крашей.
- **PE-3 Запись кода игры из потока мода во время работы игры** (наблюдение «переписать откатанный сайт», `SetPersistentSessionPatches`,
  `mod:661-688`): 5-байтовые jmp/call пишутся не атомарно, без остановки потоков игры → поток игры может выполнить полузаписанную
  инструкцию. Гипотеза (= SN-13), окно малое.
- **PE-4 Убранная 12-с задержка респауна меняет тайминги, на которые рассчитан BBSC** (сделан на shadPS4 без этого патча): смерть/вайп/
  загрузки идут быстрее, а у BBSC фиксированные окна (curtain 2.5 с, death lock 15 с, wipe settle 2 с, follow after load 5 с —
  `re:7240-7243`, `re:8068`, `re:4000`, `re:4925`). Гипотеза; проверить по логам смертей в коопе с `BB_RESPAWN_DELAY_FIX=0` и без.
- **PE-5 Пересечения проверены только по адресам из скрипта.** `overlap.py` берёт сайты порта из вписанного вручную списка + `patches.bin`;
  новые хуки порта (engine_features) туда сами не попадут. Стоит превратить проверку в тест (в `bloodborne_pc/tests`). Низкий.
- **PE-6 Слот импорта чтения геймпада** перехватывают и мод (`mod:864-880`, ждёт до 60 с, пока слот укажет вне образа), и, возможно,
  порт (`runtime_pad.c`) — порядок установки зависит от времени. Не проверено, гипотеза.
