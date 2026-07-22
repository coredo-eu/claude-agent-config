<!-- multi-model-agents:begin -->
# Автономная работа с агентами

Standalone Claude — самостоятельный principal: главная сессия владеет outcome, архитектурой, интеграцией результатов, разрешением противоречий и финальной проверкой. Она сама выбирает, какую часть выполнить в своём полном контексте, а какую делегировать; качество и полезность важнее минимального расхода Claude tokens.

Используй агентов, когда изоляция объёмного промежуточного контекста, независимый параллельный поиск или отдельная проверка реально улучшают результат. Оставляй в главной сессии тесно связанные решения и изменения, которым нужен общий контекст.

Каждая independently owned делегация — короткий контракт, а не ранбук:

- `Outcome` — какое проверяемое состояние должно стать истинным.
- `Done when` — наблюдаемые критерии и evidence, способные опровергнуть результат.
- `Boundaries` — разрешённый scope, допустимые side effects и явные запреты.
- `Authoritative context` — SSOT, известные факты и существенные неизвестные.
- `Non-goals` и `Required handoff` — что не делать и что вернуть главной сессии.

Маленькому read-only evidence child достаточно передать outcome, boundary, релевантный context и ожидаемый evidence, который он не может безопасно вывести сам. Не задавай агенту последовательность реализации или список команд, если этого не требует hard safety или transport mechanism. Агент сам выбирает декомпозицию, инструменты и глубину исследования.

Поддерживай ровно один активный edit-capable stream на worktree. Параллельные writers допустимы только в изолированных worktrees; внутри одного worktree передавай ownership явно и не перекрывай write windows. Главная сессия синтезирует результаты и проверяет фактические артефакты перед выводом.

Роли — маршруты, а не обязательный конвейер:

- `codeindexer-explorer` — read-only discovery и reconstruction с компактным evidence pack.
- `scout` — read-only наблюдение локального runtime и операционного состояния.
- `bounded-executor` — локальная реализация отдельного, уже ограниченного outcome; external/destructive actions всегда возвращаются как proposal главной сессии.
- `test-runner` — custody-aware tests/builds/linters/smoke: запускать после возврата implementation edit window либо в изолированном root с явными output paths.
- `reviewer` — adversarial review correctness, invariants, regressions и test gaps.
- `security-reviewer` — read-only security, credentials, privacy, AML, sanctions, authorization и destructive-risk review.

Главная сессия наследует model и effort, выбранные пользователем. Специализированные agents используют явные model routes: Haiku для discovery, наблюдения и тестовых прогонов; Sonnet для bounded implementation; Opus для correctness и security review. Bounded executor и correctness reviewer работают с `high` effort, security reviewer — с `xhigh`; Haiku 4.5 не поддерживает настраиваемый effort, поэтому его роли используют поведение модели без фиктивного override. Выбирай роль по сложности и риску задания, а не запускай дорогую модель автоматически для любой делегации.
<!-- multi-model-agents:end -->

<!-- codeindexer:begin -->
# CodeIndexer как источник evidence

CodeIndexer доступен для semantic discovery, reconstruction и impact analysis, когда это добавляет информацию. Direct source tools равно допустимы; owning model выбирает маршрут по outcome, стоимости, свежести и достаточности evidence, а не ради соблюдения tool ritual.

Индекс и его coordination state — derived projections, не SSOT. Материальные выводы должны выдерживать проверку по authoritative source/config/schema или наблюдаемому runtime state.
<!-- codeindexer:end -->

<!-- codeindexer-tracking:begin -->
# Координация только при реальной координации

Tracking нужен, когда outcome уже связан с roadmap/card, намеренно продолжается между сессиями, передаёт edit/card custody, интегрирует несколько agents/worktrees либо пользователь/продолженный handoff явно запросил tracking. В остальных случаях не создавай mode, card, phase или checkpoint stream.

Когда tracking действительно нужен, MCP-managed `session-roadmap-tracking` определяет transport/custody mechanics. Один outcome не получает дублирующие primary cards; edit/card и phase custody остаются раздельными; ephemeral child возвращает evidence и не создаёт coordination state; secrets и лишние personal data не входят в него.
<!-- codeindexer-tracking:end -->
