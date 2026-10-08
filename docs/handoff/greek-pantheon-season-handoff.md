# Content Factory — handoff: Greek Pantheon season

Дата handoff: 2026-10-08
Репозиторий: sebastiansayama-boop/content_factory
Основной продукт: Content Factory
Telegram test channel: AtlasOpenLab

## 1. Рабочее правило

Архитектурный этап считается завершённым.

Рабочий цикл:
реальный сценарий → запуск → фактический результат/ошибка → минимальное изменение → повторный запуск → внешняя проверка.

Не проектировать новую архитектуру ради гипотетических рисков. Не превращать локальную задачу в исследование платформы. Любое утверждение «работает», «опубликовано», «готово» должно опираться на конкретный результат GitHub Actions, ContentRun, HTTP/UI/Telegram или теста.

Предпочтительный порядок:
GitHub → тест/запуск → deploy → фактическая проверка → минимальный fix → следующий сценарий.

Отдельно разделять:
- факт;
- вывод;
- гипотезу;
- неизвестно.

## 2. Что было сделано в этом цикле

Создан и последовательно опубликован сезон:
«Пантеон богов в Древней Греции».

Фактическое состояние библиотеки после завершения:
- файл: library/telegram/greek-pantheon-series.json
- series_id: telegram-series-greek-pantheon-004
- episode_count: 16
- published: 16/16
- READY: 0
- Telegram message IDs: 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172
- последний ContentRun: run-16cfed21-da6b-4a9b-9298-baad04fcc898
- последний commit записи публикации: eef899dbb61b2832dde979a17afb1504925c1221
- временный trigger удалён: 0f314db80ba98ffa86d7a6996fbd2bbfd8dfcbf1

Важно: первоначально план обсуждался как 15 эпизодов, но при финальной проверке в library обнаружился 16-й эпизод со статусом READY и story_state.next_required_transition = «Завершение сезона». Поэтому фактический сезон оказался из 16 эпизодов. Он также опубликован.

## 3. Доказанный Telegram E2E путь

Использовался:
- library/telegram/greek-pantheon-series.json
- scripts/publish_telegram_library.py
- .github/workflows/publish-telegram-episode.yml

Publisher:
1. явно получает номер TELEGRAM_EPISODE;
2. читает нужный episode из library;
3. создаёт ContentRun;
4. формирует package;
5. approve;
6. publish;
7. проверяет финальный ContentRun = PUBLISHED;
8. повторный publish проверяется на idempotency;
9. workflow печатает:
   TELEGRAM_EPISODE_N_RUN_ID
   TELEGRAM_EPISODE_N_MESSAGE_ID
   TELEGRAM_EPISODE_N_STATUS=PUBLISHED
   TELEGRAM_EPISODE_N_REPLAY_IDEMPOTENCY=PASS

В этом сезоне все 16 эпизодов дали STATUS=PUBLISHED и REPLAY_IDEMPOTENCY=PASS.

## 4. Фактическая последовательность публикаций

1 → message 157
2 → 158
3 → 159
4 → 160
5 → 161
6 → 162
7 → 163
8 → 164
9 → 165
10 → 166
11 → 167
12 → 168
13 → 169
14 → 170
15 → 171
16 → 172

Telegram:
https://t.me/AtlasOpenLab

## 5. Что важно проверить в новом цикле

Не предполагать, что «накопление опыта» уже означает обучение модели.

В Content Factory ранее был добавлен ExperienceRecord:
- ACCEPT → SFT candidate
- EDIT → generated→final, SFT / потенциально preference
- REJECT → rejected candidate, DPO только при наличии chosen
- REGENERATE → lineage
- QC → quality metadata

Но ExperienceRecord сам по себе является persistence-слоем. Автоматического retrieval/injection этих записей в последующую генерацию считать доказанным нельзя без проверки реального кода и E2E сценария.

Следующая задача — изучить, что реально накопилось после 16 публикаций:
1. какие ExperienceRecords созданы;
2. какие поля реально заполнены;
3. связываются ли они с ContentRun;
4. используются ли они при следующей генерации;
5. есть ли реальный feedback loop;
6. что является просто историей публикаций, а что уже является обучающим примером.

## 6. Известные технические наблюдения

Во время сезона был замечен технический шум вокруг workflow:
- некоторые jobs долго находились в queued;
- один из ранних запусков episode 3 попал в другой workflow и завершился failure, но отдельный корректный путь публикации episode 3 был успешно выполнен;
- в одном из логов встречалось несоответствие TELEGRAM_LIBRARY_PATH и commit message.

Это не повод заранее менять архитектуру. Следующий чат должен сначала воспроизвести/проверить фактический сценарий и только при наблюдаемой проблеме предлагать минимальный fix.

## 7. Источники серии

Основные источники, записанные в library:
- Metropolitan Museum of Art — Greek Gods and Religious Practices
- Metropolitan Museum of Art — Death, Burial, and the Afterlife in Ancient Greece
- Metropolitan Museum of Art — Mystery Cults in the Greek and Roman World
- World History Encyclopedia — The 12 Olympian Gods

## 8. Контекст Content Factory

Целевой поток:
Тема → Research → Accept knowledge → Generate → text/images → Edit/Regenerate → Export/Publish.

Общий lifecycle:
INTENT → RUN → KNOWLEDGE / RESEARCH / RULES → RESEARCH → EDITORIAL → CONTENT BRIEF → PRODUCTION PLAN → EXECUTION → ARTIFACTS → QC → REVIEW → DISTRIBUTION → OUTCOME → LEARNING

Информационный поток:
SOURCE → EVIDENCE → CLAIM → EDITORIAL POINT → CONTENT ELEMENT → ARTIFACT → PUBLICATION

Trace:
INTENT → RUN → STAGE → TASK → TOOL → ACTION → RESULT → DECISION

Детерминированный код должен отвечать за правила, persistence, actions, provenance, QC и lifecycle. LLM — за интерпретацию, классификацию, extraction и generation.

## 9. Правило для нового чата

Не начинать с нового дизайна системы.

Сначала:
1. прочитать этот handoff;
2. самостоятельно изучить актуальный GitHub repository;
3. проверить реальные файлы, workflows, publisher, tests и последние commits;
4. сопоставить код с фактическими результатами сезона;
5. только после этого сформулировать следующий рабочий шаг.

Если обнаружено расхождение между handoff и текущим repository — repository является источником истины, а расхождение нужно явно отметить.

---

# ЗАДАНИЕ ДЛЯ НОВОГО ЧАТА

Ты продолжаешь работу над Content Factory после завершения сезона «Пантеон богов в Древней Греции».

Сначала самостоятельно изучи актуальное состояние репозитория sebastiansayama-boop/content_factory через GitHub. Не полагайся только на этот handoff.

Проверь:
- library/telegram/greek-pantheon-series.json
- scripts/publish_telegram_library.py
- .github/workflows/publish-telegram-episode.yml
- связанные Telegram tests
- ExperienceRecord implementation
- последние commits после публикации episode 16
- реальные workflow results, если они доступны.

Главный вопрос нового цикла:

«Что реально накопил Content Factory после 16 последовательных публикаций и может ли этот накопленный опыт использоваться в следующем поколении контента?»

Исследуй именно фактический механизм, а не желаемую архитектуру.

Нужно установить:

A. Persistence
- сколько ExperienceRecords реально создано;
- какие decision types встречаются;
- какие run_id/example_id присутствуют;
- какие prompt/context/generated/final/edits/qc/provenance поля заполнены.

B. Lineage
- можно ли связать публикацию → ContentRun → package → approval → ExperienceRecord;
- сохраняется ли связь между generated и final;
- сохраняется ли связь regenerate → source run.

C. Retrieval / learning
- читаются ли ExperienceRecords при следующей генерации;
- попадают ли они в prompt/context;
- есть ли ranking/filtering;
- используется ли feedback реально или только хранится.

D. Training readiness
- какие записи уже можно превратить в SFT examples;
- какие в preference/DPO examples;
- чего не хватает для полноценного обучающего датасета;
- есть ли уже собственные данные/веса или пока только dataset/persistence.

E. E2E proof
Если код позволяет, выбрать минимальный реальный сценарий:
предыдущий опыт → новая генерация → проверить, что опыт действительно использован.

Не делать архитектурный рефакторинг заранее.

Формат результата:

1. Факты из repository.
2. Факты из реальных тестов/workflows.
3. Что уже работает.
4. Что только хранится.
5. Что НЕ используется генерацией.
6. Минимальный следующий шаг.
7. Если нужен код — изменить только необходимое и проверить E2E.

Обязательно сверяй ключевые технические выводы с внешними источниками, если речь идёт о современных подходах к SFT/DPO, Experience Replay, preference datasets или обучению LLM.

Не считай публикацию доказательством обучения модели. Не называй persistence «learning», пока не найден реальный retrieval/training path.

Начни с исследования repository и фактического состояния после episode 16. Не проси меня повторять контекст, если его можно получить из repository.
