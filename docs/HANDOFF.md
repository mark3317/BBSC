# HANDOFF — состояние работы и что дальше

> **T17 deployed PC + laptop:** event-driven reward/drop/cutscene/departure
> notifications, numeric scaling/cache and research-only diagnostic scans (`addfd08`).
> Build exit=0, zero warnings; 12 deployed-file hash checks PASS; concurrency,
> scaling and existing recovery/follow checks PASS. Research OFF, saves unchanged.
> User reports gameplay generally works. Run 20261030-161747: PC crash coincides
> with nvlddmkm 153 + WER LiveKernelEvent 141/Blackwell at 16:27:49; GPU TDR
> confirmed, root cause unresolved. Guest returned home and retained trip items.
> PC median 59.7 game ticks/s; no matched baseline for speedup. See [T17](fixes/T17-event-work.md).


> **T16 deployed PC + laptop**: consume host arrival after sharing map, preventing repeated
> follow loads on Cathedral Ward border. Code c75b1d6, tests PASS, build exit=0.
> Host crash confirmed Windows GPU TDR 141/nvlddmkm Blackwell, not fixed by this patch.
> See [T16](fixes/T16-follow-border.md). Saves unchanged.

> **T15 deployed to PC + laptop**, override and active-package hashes verified.
> See [T15](fixes/T15-loading-and-NPCs.md). Gameplay confirmation pending.
> **User preference:** after future fixes and successful builds, deploy immediately to
> PC/laptop where the game and launcher are stopped. Do not terminate running games;
> report devices skipped. Save rollback still requires a separate request.


> **T14, 30 October: post-load/session recovery deployed to PC + laptop by user request.**
> Latest laptop log confirms dead guest after wipe load, then home state=0/own_world=1
> with phantom type=1 (bell rejected player type). Cancel kept-death override before
> teardown; reconcile local character/camera after completed loads independently of
> remote creation; normalize phantom at home; dead/missing guests can return home.
> Override and active-package hashes verified on both machines. No save/settings changes.
> All 15 fixture scenarios pass; final mod build exit=0, no warnings.
> Code `8ff3435` + `7ed971b`. Details/hash in
> [T14-post-load-recovery](fixes/T14-post-load-recovery.md); gameplay confirmation pending.


> **T13, 30 October: join failed because MSI Center exhausted PC UDP ports.**
> User-authorized MSI Center restart freed 16,308 sockets; game STUN now reaches
> VPS as twin:3658. Retest join. Laptop crash separately confirmed nvlddmkm TDR/
> LiveKernelEvent 141 with upscaler/FG OFF; cause unresolved. No new code deployed.
> See [T13-connect-and-laptop-TDR](fixes/T13-connect-and-laptop-TDR.md).

> **T12, 30 October: PC startup fixed in PORT f4f0028, installed/verified on PC + laptop.**
> Signaling initialization rollback deadlocked joining a dispatch worker while
> owning its mutex. Removed unused ioctl socket; release lock before workers.
> T11 DLL + Research OFF reaches title menu; left running, no world loaded.
> See [T12-startup-signaling](fixes/T12-startup-signaling.md).

> **T11, 30 October: build 8373921 deployed/verified on PC + laptop; Research logs OFF.**
> PC restored forest-host (testHost, slot 1); current PC save subsequently copied to laptop test by user request (19 files verified, including journals).
> Host-first wipe spectator cleanup, resolved banner draw filter, native chest
> availability and immediate native summon loading screen. See
> [T11-test-regressions](fixes/T11-test-regressions.md). T10 test had Research logs
> enabled (168/168 hooks); production trace reduction was not exercised.

> **T10, 30 October: performance/notification audit, deployed to PC + laptop.**
> Diagnostic-only hot hooks are opt-in; obsolete boss-banner transport removed;
> reload-safe param slot cache, dead shop guard removed, personal-event policy
> unified. Keep connection/departure and PvP notices. See
> [T10-performance](fixes/T10-performance.md). `d101121`: mod build exit=0, zero warnings;
> regression checks passed. Deployed/verified on PC + laptop by user request; gameplay/FPS verification pending.

> **T9, 30 October: boss wipe regression confirmed in logs.** Client watchdog revived
> in place at 01:07:12, before PartyGhostDeath_2 at 01:07:13; no full client reload.
> Unified watchdog/native death state, latched boss-at-death, actual load-generation
> check, HUD cleanup after reload/return home. See `docs/fixes/T9-boss-wipe.md`.
> Code `12984a9`: build exit=0; deployed/verified on PC and laptop. SHA256
> `68943CD98A535BCEB9771F5B5DB9FCFC3DD696EDA50747D5ABECD1DE23F514AF`.
> Gameplay confirmation pending. Current saves and `forest-host` remain untouched.

> **Запомненный сейв «в лесу» (30.10):** снимок **`forest-host`** на ПК,
> `D:\Games\Bloodborne\coop-dev\saves\forest-host`.
> Источник — `testHost`, активный слот **1 по BBSC**; хост в **Запретном лесу**,
> лампа **2702950**. По просьбе «откати к сейву в лесу» использовать именно этот
> снимок на ПК, не `start-clinic-teststart` и не `before-amelia-host`.
> Сохранены весь SPRJ0005/метаданные, bell-pending и item-ledger; 14 файлов сверены,
> SHA256 — `forest-host/sha256-manifest.json`. Ноутбук не откатывался.
>
> **Контроль без FG:** пользователь сообщил, что игра шла нормально, но выход хоста
> в меню снова завершился крашем. В 00:42:52 — nvlddmkm 153, WER 141 / Blackwell,
> `frame_gen=off` подтверждён в ini; DLSS upscaler остаётся включён.
> Поэтому FG не является необходимым условием наблюдаемых сбоев; причина не установлена.
> Прогон `20261030-003555`, подробности — `docs/fixes/T8-GPU-crash.md` § «Контроль без FG».

> **30.10, T8 GPU:** два TDR RTX 5070 на ПК-хосте с DLSS FG (00:21 и 00:28),
> WER LiveKernelEvent 141 / nvlddmkm.sys. Разбор — `docs/fixes/T8-GPU-crash.md`.
> На ПК для контрольного теста выключена только Frame Generation (`frame_gen=off`),
> DLSS upscaler и ваншот оставлены; сейвы не откатывались. Связь именно с FG пока гипотеза.
> После краша на ноуте сработали уведомление об уходе хоста, завершение сессии и возврат
> домой; доступность лампы ещё не подтверждена пользователем. Мод остаётся 260b64f.

> **T8, 2026-10-30:** T7 подтвердил дверь после собаки и отсутствие красной ленты.
> Остались ранняя белая лента (авто-pickability перекрывает запрет скрипта), потеря
> ключевых на новом призыве (очищенный журнал + фантомная сумка), завершение при меню/краше.
> Исправления и доказательства — `docs/fixes/T8-rejoin-quit.md`. Мод + relay-сервер;
> перед изменениями VPS его исходник сравнен с репо: различались только окончания строк.
> Код `260b64f` (включает e9baa51/d6e4ff7): сборка `exit=0`, 8 предупреждений,
> установлен на ПК и ноут; SHA256 `13B6AFF1A75A2D18D06B9E56EAABDA96C48F47246A503ECDCBD4F7872B94487D`
> совпадает во всех активных копиях. Сервер обновлён, сервис активен, TCP 20444 слушает;
> бэкап `/opt/bbsc/backups/t8-20261029-211454`. На обеих машинах чистый `start-clinic-teststart`,
> 14 файлов сверены; журналы сохранены как `*.before-t8-*`. Сейвы до отката:
> ПК `_auto-20261030-001559`, ноут `_auto-20261030-001602`.
> Прогон `20261030-001822` начат; ждём игрового теста, поведение ещё не подтверждено.

> **T7: лента до квеста и дверь с собакой.** Причины найдены в host-only событиях
> 12410702 и 12410748. Исправлены локальные квестовые события (16 по данным игры)
> и ложная ретро-выдача по служебным флагам ItemLot (красная лента 72410410).
> Подробности, ограничения и тест — `docs/fixes/T7-quest-gates.md`.
> Код `d68d03f`: сборка `exit=0` (8 предупреждений), установлен на ПК/ноут;
> SHA256 `DD48F3C5B6A54997A6F36279BDC605AAD1D3CC623A365A56EA9B9B60EC30EA03` совпадает.
> На обеих машинах восстановлен `start-clinic-teststart`, 14 файлов сверены;
> поздние журналы отложены в `*.before-t7-*`, сейвы до отката — `_auto-20261029-233803`
> (ПК) и `_auto-20261029-233810` (ноут). Прогон `20261029-233825` начат, ждём теста.

> **Тест 6, 2026-10-29 23:00–23:22 МСК:** `e40ede7` собран и установлен на ПК/ноут,
> хэши совпадают. На обеих машинах восстановлен `start-clinic-teststart` (персонаж `testStart`).
> Пользователь подтвердил предметы после загрузок/дома, стук, оба порядка смертей на боссе,
> клавиатуру и стик камеры. Логи собраны: `runs/20261029-225307`; детали — `docs/fixes/T6-results.md`.
> Осталось `?ActionEventInfo?` у гостя при возрождении (P3). Life-членство, одновременные
> NPC-действия, три игрока и длительное наблюдение остаются отдельными проверками.
> Ниже сохранена история; формулировки «не раскатано/не проверено» про e40ede7 и T5
> заменены этим результатом в пределах перечисленных сценариев.

> **Продолжение T5:** штатный NetworkSync отключён для трёх обработчиков стука;
> вайп берёт карту+позицию из follow хоста; возрождение другого гостя не считается возрождением хоста.
> Доказательства адресов, ограничения и дополнительные проверки — T5-results §8.
> Игровой проверки и деплоя не было.

> **T5, 2026-10-29:** правки предметов, смертей, точки гостя, NPC и SDL-ввода камеры.
> Сборка `build/mod/` успешна (`exit=0`); подробности, ограничения и чек-лист — `docs/fixes/T5-results.md` §7; полный аудит 507 пар
> (194 события) — `docs/fixes/T5-event-owners.txt`. Деплой и игровой тест не выполнялись.
> Не считать пункты проверенными в игре. Отдельно проверить одновременные NPC-действия
> и выход живого участника при мёртвом хосте.

Последнее обновление: 2026-10-29 (сессия «K2 предметы гостя, PT-9, смерти на боссе», затем T4 этапы 1–3).

> **2026-10-29, T4:** по тесту 4 (`docs/fixes/T4-results.md`) сделаны этапы 1 (`659b826`: спам лога Сна, возврат
> предметов поездки после каждой загрузки и дома, свой мир сразу при загрузке после вылета, катсцена один раз) и
> 2 (`3081a08`: профайлер `BBSC perf:`, сброс лога раз в 250 мс, исследовательские логи под «Research logs» —
> `docs/fixes/PERF.md`). Этап 3 — только исследование Сна: `docs/fixes/DREAM.md`, рекомендация — вариант (а)
> «гость видит свой Сон» — **пользователь выбрал (а), сделано** (`SHADPS4_BBSC_DREAM_OWN`, по умолчанию вкл., `DREAM.md` §5).
> Не раскатано и не запушено. Чек-лист теста — T4-results §6.

> **2026-10-29, позже:** после теста 3 (`docs/fixes/T3-results.md`) собрана сборка A+B: мод не удаляет и не блокирует предметы; дома только лог; выдача «положенного» и ретро — при принятии призыва в своём мире; исследовательские логи ключевых предметов; правки шторки и обложки; лог ввода камеры. Не раскатана. Чек-лист — `docs/fixes/K2-items.md` §10, разбор — `docs/fixes/K2-snapshot-plan.md` §4.
Начни с этого файла, затем `docs/BACKLOG.md`, `docs/fixes/K2-items.md`, `docs/RESEARCH-NOTES.md` (раздел 2026-10-29).

## 1. Где всё лежит сейчас

| Что | Состояние |
|---|---|
| Ветка `mark/bbport-fixes` | коммиты сессии: `2d3e0c9` (журнал предметов), `d2e3ad4` (дубли дропа), `6d62363` (ключи + проверка при входе), `33a8751` (PT-9 kept-home), `dd57483` (смерти, заглушка, мышь камеры), `0bfbc0a` (слежение за ключевыми дома, Сон после вайпа, I/J/K/L), плюс `41e2ad0`, `3a095c2` (A+B), `659b826` (T4 этап 1), `3081a08` (T4 этап 2, perf) и коммит документов. **Запушено до `2d3e0c9`, остальное — нет.** |
| ПК (хост) | раскатан `dd57483` (не последний!). **user_dir лаунчера переключён на `D:\Games\Bloodborne\testHost`** (было `ddd`; бэкап `%APPDATA%\bbport-launcher*\settings.json.bak-coopdev`). Перед игрой с друзьями вернуть `ddd`. |
| Ноут (гость) | раскатан `dd57483`. Журналы прошлых прогонов отложены: `...\bbsc\guest-items\taken-sd1-1.bin.bak-k2test`, `...\bbsc\item-ledger\ledger-sd1-1.bin.bak-k2test` (на ПК — `ledger-sd1-{0,1}.bin.bak-k2test`). |
| Снимки сейвов | `k2-before-test` на ПК (testHost) и ноуте (test) — состояние до тестов K2; `_auto-*` — автоснимки перед откатами. |
| Прогоны | `bloodborne_pc/out/coop-dev/runs/20261029-055243` (тест 1), `runs/20261029-040355` (тест 2, имя в UTC). |

**Важно про окружение этой сессии:** Claude работал прямо на mark-pc (Windows, Git Bash/PowerShell), а не в Linux-VM. `coopdev.sh` рассчитан на VM (ssh к `mark_pc`), поэтому шаги делались вручную:
`powershell -File bloodborne_pc\tools\coop-dev\coopdev.ps1 -Action <status|deploy-mod|save-snap|save-restore|set-user-dir|collect> -Install D:\Games\Bloodborne\bbport-coop ...` для ПК;
для ноута — `scp` скрипта и сборки в `C:\Games\Bloodborne\coop-dev\` + `ssh local_pc powershell -File ...coopdev.ps1 -Action ...`. Начало прогона (`run.txt`) и сбор логов VPS — вручную (см. `cmd_test` в coopdev.sh).

## 2. Что сделано и проверено

| Тема | Итог | Проверка |
|---|---|---|
| Повторная выдача «Нечистоты»/Посоха Лиги хосту (PT-5) | флаг получения своей награды (6676/6678) больше не откатывается охраной NPC-флагов; повтор одноразового уникального лота блокируется (K3) | причина CONF по логу хоста 27.10; повтор в игре ещё не проверен |
| Журнал предметов (K2) | `item-ledger/ledger-<user>-<slot>.bin`, CHECK-строки `BBSC CHECK FAIL/OK <класс>` | работает: тесты 29.10 |
| Дубли дропа с врагов | BBSC не выдаёт `isGuestDrop` (флаконы, пули) — их игра кладёт на труп; самоцвет из лота — одной ванильной наградой записи | тест 2: дубля нет |
| Ключевые предметы гостя пропадают (PT-1) | T4: игра восстанавливает фантомную сумку на **каждой** загрузке в мире хоста и дома; снимок не найден. `659b826`: возврат подобранного в поездке после каждой загрузки (3 с) и дома (5/30/60 с), `K2-lost-at-load` / `K2-lost-on-trip-home … put back` | **не проверено** (T4-results §6) |
| Выход печатью без загрузки домой (PT-9) | защита SN-kept-home; в тесте 2 выход прошёл нормально | триггер не пойман повторно |
| Заглушка с логотипом (PT-4) | BBSC больше не открывает экран загрузки сам | тест 2: заглушки нет |
| Камера наблюдения | мышь — работает (тест 2); I/J/K/L — исправлено в `0bfbc0a` | клавиши и геймпад не проверены |
| Мёртвый гость, хост не перезагрузился 45 с (PT-2) | гость сначала выходит из сессии, потом своя перезагрузка | не проверено |
| Вайп → Сон охотника (PT-12) | откат смены точки возрождения на лампу Сна, пока мёртв | **не проверено** (`0bfbc0a`) |

## 3. Открытые вопросы (по приоритету)

1. **Механизм отката инвентаря фантома.** ⚠ Поправка 2026-10-29 (`docs/fixes/K2-snapshot-plan.md`): откат **не** «целиком» — в том же сейве шкатулка этой поездки есть, пропала только лента (goodsType 1); снимок `0x0131E5C0` — это мир, не инвентарь; защита могла пропустить удаление (молчит вне окна 8 с). Главный кандидат — обработчик сообщений инвентаря `0x014D3DC0` (сообщение 25 чистит сумку, 24 возвращает ключевые по списку). План — исследовательская сборка с логами (этап A там же). Исходная запись: CONF по сейвам: после конца сессии игра восстанавливает инвентарь гостя из снимка, сделанного при входе, целиком (ни одного вызова 0x014D94A0/0x014DAB20), в плавающий момент (тест 1 — сразу при 6→0 без загрузки; тест 2 — позже 5 с после загрузки домой, но до сейва через 28 с). Пропадают ключевые предметы (лента 4903); флаконы/пули/осколок/шкатулка остались — проверить, все ли goodsType 1 или «предметы, полученные фантомом». Пользователь хочет **не выдавать ничего дома** — нужен настоящий фикс: найти снимок (кандидаты: `0x0131E5C0` «freezes own world into the save snapshot», `global+0x1698/+0x16B8/+0x16D8`, сейв-писатель `0x0156AA50`) и либо дописывать подобранное в снимок, либо не давать восстанавливать. Тогда убрать слежение дома и защиту на 0x014D94A0/0x014DAB20 (она ни разу не сработала, а висит на горячих функциях).
2. **Кто меняет точку возрождения на Сон при вайпе** (`global+0x1528`, ~5 с после смерти хоста). Кандидаты из комментария `TickBbscRespawnPointWatch`: 0x012F8259 (lamp update), 0x019423A0 (travel), 0x0131E4A0, 0x01312FF0, 0x01321440, 0x01338340 — поставить хуки с логом вызывающего.
3. **PT-9: что запускает решение «покинуть комнату»** (`0x01941C20` OwnWorldStep, stage request 4, без lua-события, сеть в порядке). Сейчас сессия завершается (`SN-kept-home`); лучше было бы вернуть гостя к хосту. Смотреть captures `OwnWorldStep` / `Persist.SkippedCleanup` при повторе.
4. **PT-10:** хост после перезахода в точке старта (клиника Иосефки). В том запуске было два персонажа (слоты 0 и 1). Нужен повтор.
5. Самоцветы/руны гостю через ванильную награду в мире хоста — путь не проверен (`K2-award-nothing` = запасной путь BBSC).
6. **Сон у гостя** — вариант (а) «свой Сон» сделан, ждёт теста; после теста удалить старый код Сна хоста (`DREAM.md` §5).
7. **Производительность** — по первым строкам `BBSC perf:` из теста перевести дорогие тики на 100–500 мс (`docs/fixes/PERF.md` §5).
8. Из BACKLOG: PT-6 (катсцены дважды — сделано в `659b826`, ждёт теста), PT-7 (стук в окна NPC), PT-8 (жест в инвентаре), WS-5, PT-3 (GPU TDR).
9. Друзья с сейвом `ddd`: инструмент мастерской рун у гостей — обход «инструменты как общие ключи» оставлен; ретро-починка сработает только если у них записался `guest-items/taken-*.bin`.

## 4. Решения пользователя (держаться их)

- Предметы у каждого игрока **свои**, подбираются сразу в мире хоста; **минимум выдачи гостю за действия хоста**; у гостя и хоста равные права.
- **Ничего не выдавать гостю после возвращения в свой мир**, если это возможно; проверка «все ли предметы есть» — при подключении к хосту. (Сейчас дома есть тихий возврат подобранных ключевых — вынужденно, см. §3.1.)
- Подарки разговоров — только за свой разговор (руна Валтра не раздаётся гостям, если вступил только хост).
- Ретро-починка: ключи, инструменты, значки, чаши (не расходники, не квестовые предметы для NPC).
- Повтор одноразового лота: блокировать + `CHECK FAIL K3-repeat`.

## 5. Ближайший тест — `docs/fixes/T4-results.md` §6 (последний коммит ветки)

Ниже — старый план для `0bfbc0a`, оставлен для истории.

### 5.0 (устарело) Тест сборки `0bfbc0a`

Раскатать `0bfbc0a`, откатить сейвы к `k2-before-test`, отложить `guest-items`/`item-ledger` гостя (как в прошлый раз), хост — **слот 1**.
1. Гость подбирает Белую ленту → выход печатью домой → 2 мин стоит. Ждём `K2-lost-on-trip-home … at home N s … put back` (N — момент отката) и ленту в инвентаре; затем выйти в меню и перезайти — лента в сейве.
2. Вайп на Чудовище-клирике: гость умирает первым (камера: мышь, I/J/K/L, стик), потом хост. Ждём `CHECK FAIL DEATH-dream-respawn` у хоста и пробуждение у лампы Центрального Ярнама, не в Сне.
3. Повторная загрузка Запретного леса хостом с вступлением в Лигу — руна «Нечистота» не множится (если дойти).
Логи: `grep -h "BBSC CHECK\|BBSC ledger\|BBSC items\|respawn point" bbsc-mod-*.log`.

### T11 follow-up: copy PC forest save to laptop
User requested the current PC save on the laptop. Source snapshot
`pc-forest-transfer-20261030-111920` created from PC testHost; restored to
`C:/Games/Bloodborne/test/savedata/1/CUSA00207/SPRJ0005`.
Save/system metadata and current own-world, bell-pending, item-ledger, guest-items,
shared-progress, kit-repaired directories synchronized; missing source journals
become empty on target to prevent old guest recovery from overwriting imported state.
19 files verified by SHA256. Laptop's old save and all journals backed up in
`C:/Games/Bloodborne/coop-dev/saves/before-pc-forest-20261030-111954`.
Both games were closed. Mod and Research settings unchanged.
