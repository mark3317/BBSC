# OPEN-QUESTIONS — что проверить / спросить у автора

Составлено 2026-10-29 по файлам областей. Порядок — по пользе для FINDINGS.

## Проверить на машинах (только чтение)
1. **Ноутбук-гость (LA-1/GI-2):** есть ли `%LOCALAPPDATA%\bbport-coop\...\bbsc\own-world\own-*.bin`, `shared-progress\pending-*.bin`,
   `guest-items\taken-*.bin`? В логах гостя — строки «own world: kept before the join load», «BBSC shared progress», и нет ли повторяющегося
   «no save written in this run yet». Значение `BBSC_SAVE_DIR` в env запуска (лог лаунчера).
2. **Логи гостя (SN-08/WS-6):** как часто встречаются «no flags from the host for map … following with our own» и «no fresh host flags for other areas yet»?
3. **Сервер/клиент (SN-02/WS-7/SN-18):** «too slow (… bytes waiting)» в логах gameserver, «the server is not taking our frames» в логах мода,
   переходы relay → P2P-канал во время сессии.
4. **VPS:** запущен ли `bbsc-gameserver` с `--relay-session-routing` (unit-файл)? Сколько одновременных клиентов relay обычно?
5. **Диск (GI-3/LA-2):** размер `save-backups` и `<user_dir>\coop-backups` на ноуте.

## Вопросы автору (решения по дизайну)
6. **Shared Progress выключен** — должны ли свои квесты (журнал разговоров), предметы разговоров и home awards всё равно доходить домой (WS-3)?
7. Журнал разговоров и home awards — писать на диск, как own-world/pending progress (WS-2)?
8. Чаши (область 29) в Shared Progress — исключать, как в рассылке «других» блоков (WS-1)?
9. Какой смысл у kind 1 флагов, которые могут **сбрасываться** (лифты/рычаги/фазы) — нужен список исключений для OR (WS-9)?
10. Talk-driven событие «не наше»: глушить все флаги или только NPC-квестовые (WS-5, комментарий и код расходятся)?
11. Сейв гостя во время сессии пишется из живой таблицы или из own-world snapshot (WS-8) — какой комментарий верен?
12. Ключи/жетоны: давать ли инвейдерам; сбрасывать ли состояние прошлого хоста (WS-4)?
13. «Партнёр пропал» в группе 3+ — снимать фантом по каждому участнику, а не по «никого нет» (SN-05)? 90 или 180 с (доки vs код)?
14. Катсцены хоста у гостя: какие аргументы запроса реально указатели (SN-01)?
15. `BbscReplayRoomMembers` в моде — заглушка намеренно (SN-17)?
16. Override нашей сборки после обновления официального BBSC — предупреждать или блокировать обновление (LA-3)?
17. Где единый источник правды протокола и списков флагов: `BBSC/bbport/*.patch` vs `bloodborne_pc/gpu/bbnet/vendor` (PE-1), `net_flag_watch.h` vs `bloodborne_re.cpp` (HI-1)?
18. Тайминги смерти/загрузок BBSC проверялись на bbport с убранной 12-с задержкой респауна (PE-4)?
19. Research-трассы (`BbscResearchSetFlagHook`, gift trigger watch) — оставлять в релизе?

## Не изучено (если понадобится)
- Награды боссов и дропы врагов гостю, loot view, item survey (`re:10590-10760`, `re:10947+`, `re:6694-6830`, `re:13184-13400`).
- bbhost_service, signaling в патче/форке, `bbsc_http.cpp` (кандидаты SN «по заметкам»).
- QML-страницы и мастер установки лаунчера; `pc_menu.c`, `runtime_*.c` порта.
- `docs/WORLD-SYNC.md` и CHANGELOG не сверялись с кодом.
