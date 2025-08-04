# Symbolic Physics v0.4 — проект и архитектура / Projekt und Architektur

## 1. Цель / Ziel

**RU:** Построить управляемую, самонастраивающуюся символическую физическую платформу, где физика выражается не через непрерывные уравнения, а через дискретные символы, их отношения и стохастические трансформации. Система должна:
- Автономно генерировать, удерживать и трансформировать динамику (колебания, чувствительность, адаптацию);
- Предоставлять средства анализа (reservoir readout, фазовые проекции, устойчивость/Ляпунов, параметрические исследования);
- Давать пользователю контроль и наблюдение через GUI;
- Быть расширяемой (топологии, метаправила, внешние входы) и прикладной (предсказание, детекция, адаптивное поведение).

**DE:** Eine steuerbare, selbstanpassende symbolische Physikplattform erstellen, bei der Physik nicht durch kontinuierliche Gleichungen, sondern durch diskrete Symbole, deren Beziehungen und stochastische Transformationen ausgedrückt wird. Das System soll autonom Dynamik generieren und transformieren, Analysewerkzeuge bereitstellen, Kontrolle über eine GUI ermöglichen und erweiterbar sein.

## 2. Архитектура системы / Systemarchitektur

### 2.1. Основные модули / Hauptmodule

- **symbolic_core.py (SymbolicEngine):**  
  **RU:** Параметризуемое ядро симуляции. Определяет символы с непрерывным состоянием, связи (`bind`, `cycle`), модификаторы (`invert`, `random_invert`, `noise_seed`, `background_noise`), механизмы decay и обратной связи; логирует все трансформации.  
  **DE:** Parametrisierter Simulationskern, der Symbole mit kontinuierlichen Zuständen, Verbindungen (`bind`, `cycle`), Modifikatoren (`invert`, `random_invert`, `noise_seed`, `background_noise`), Decay und Rückkopplung verwaltet; protokolliert Transformationen.

- **main_gui.py:**  
  **RU:** Интерфейс управления и наблюдения — запуск аналитических модулей, AutoTest с контролем и остановкой, согласованное исполнение через `sys.executable`.  
  **DE:** Steuer- und Beobachtungsschnittstelle – Ausführung der Module, AutoTest mit Stoppmöglichkeit, konsistente Umgebung über `sys.executable`.

- **Аналитические скрипты / Analyse-Skripte:**  
  `test_engine.py` (reservoir readout), `phase_visualizer.py`, `lyapunov.py`, `param_scan.py`, `network_builder.py` — реализация анализа, визуализации и расширения.  
  /  
  Umsetzung von Analyse, Visualisierung und Erweiterung.

### 2.2. Поток данных / Datenfluss

**RU:**  
- Вход: JSON-модели (`model_v04.json`, `random_net.json`), задающие начальные символы, связи и правила.  
- Процесс: `tick` обновляет состояния, применяются правила (модификаторы, связи, decay), всё логируется.  
- Выход: визуализации, логи, обученные readout-коэффициенты, таблицы режимов, метрики устойчивости.

**DE:**  
- Eingang: JSON-Modelle, die Anfangssymbole, Verbindungen und Regeln definieren.  
- Prozess: `tick` aktualisiert Zustände, Regeln (Modifikatoren, Verbindungen, Decay) werden angewendet und protokolliert.  
- Ausgang: Visualisierungen, Logs, trainierte Readout-Koeffizienten, Modus-Tabellen, Stabilitätsmetriken.

## 3. Зависимости и среда исполнения / Abhängigkeiten und Laufzeitumgebung

**RU:**  
- Требуется Python 3.10+ в виртуальном окружении.  
- Основные библиотеки: `numpy`, `scikit-learn`, `matplotlib`, `tkinter`, стандартные модули (`threading`, `subprocess`, `json`, `os`, `sys`, `math`).  
- Запуск организован через `setup_and_run.bat`; подпроцессы внутри GUI вызываются через `sys.executable` для согласованности окружения.

**DE:**  
- Erfordert Python 3.10+ in einer virtuellen Umgebung.  
- Wichtige Bibliotheken: `numpy`, `scikit-learn`, `matplotlib`, `tkinter`, Standardmodule (`threading`, `subprocess`, `json`, `os`, `sys`, `math`).  
- Start erfolgt über `setup_and_run.bat`; Subprozesse im GUI verwenden `sys.executable`, um Konsistenz der Umgebung sicherzustellen.

## 4. Оценочные метрики и поведение / Bewertungsmetriken und Verhalten

- **varA / varB:** дисперсия состояний символов — индикатор активности и устойчивости. / Varianz der Symbolzustände als Maß für Aktivität und Stabilität.  
- **Экспонента Ляпунова:** чувствительность к малым возмущениям — положительные значения намекают на сложную / край границы поведения. / Lyapunov-Exponent: Empfindlichkeit gegenüber kleinen Störungen; positive Werte deuten auf komplexe Dynamik hin.  
- **Readout MSE:** качество предсказания внешнего сигнала через внутренние состояния (reservoir computing). / Genauigkeit der Vorhersage durch das interne Reservoir (MSE).  
- **Фазовые траектории:** визуализация аттракторов (фиксации, циклы, потенциальный хаос). / Visualisierung von Attraktoren (Fixpunkte, Oszillationen, Chaos).  
- **Поведение расширенных сетей:** средняя амплитуда, runaway, структура связей. / Verhalten erweiterter Netzwerke: durchschnittliche Amplitude, Ausbruch, Verbindungsstruktur.

## 5. Риски, вероятности и меры смягчения / Risiken und Gegenmaßnahmen

| Риск / Risiko | Вероятность / Wahrscheinlichkeit | Последствие / Folge | Митигирующая мера / Gegenmaßnahme |
|---------------|----------------------------------|----------------------|-----------------------------------|
| Разные интерпретаторы при подпроцессах / unterschiedliche Interpreter | Средняя / mittel | Отсутствие зависимостей, сбои / Fehler durch fehlende Abhängigkeiten | Использование `sys.executable`, проверка и установка / Nutzung von `sys.executable`, Prüfung und Installation |
| Runaway в сети / Runaway im Netzwerk | Средняя / mittel | Числовой разгон, overflow / numerische Explosion | Клиппинг / нормализация / Clipping / Normalisierung |
| Зависание GUI при тяжёлых вычислениях / GUI hängt | Высокая / hoch | Потеря отклика / Verlust der Reaktionsfähigkeit | Изоляция в потоках, Stop AutoTest / Threads, Stop AutoTest |
| Битые входные JSON / beschädigte JSON | Средняя / mittel | Прекращение анализа / Abbruch der Analyse | Валидация и логирование / Validierung und Logging |
| Хаотичность на границе / Chaos an der Grenze | Предсказуемо / vorhersehbar | Потеря интерпретируемости / Verlust der Interpretierbarkeit | Параметрический скан, градуированное увеличение / Parameterscan, graduelles Anheben |

## 6. Применения / Anwendungen

- **RU:** Reservoir computing для прогнозирования временных рядов.  
  **DE:** Reservoir Computing zur Zeitreihenprognose.  
- **RU:** Детекция аномалий через дивергенцию траекторий.  
  **DE:** Anomalieerkennung durch Trajektoriendivergenz.  
- **RU:** Процедурная генерация контента с вариативностью.  
  **DE:** Prozedurale Inhaltserzeugung mit Variabilität.  
- **RU:** Внутренние состояния агента управляют поведением.  
  **DE:** Interne Agentenzustände steuern Verhalten.  
- **RU:** Метаправила и адаптивная топология.  
  **DE:** Meta-Regeln und adaptive Topologie.

## 7. Дальнейший план / Weiterer Plan

### Краткосрочно / Kurzfristig

1. **RU:** Фикс автозапуска и согласованного окружения в GUI.  
   **DE:** Fix des Autostarts und der konsistenten Umgebung.  
2. **RU:** Интерактивные слайдеры параметров.  
   **DE:** Interaktive Parameter-Slider.  
3. **RU:** Нормализация случайных сетей.  
   **DE:** Normalisierung zufälliger Netzwerke.

### Среднесрочно / Mittelfristig

1. **RU:** Онлайн readout с визуализацией ошибки.  
   **DE:** Online-Readout mit Fehlervisualisierung.  
2. **RU:** Кластеризация аттракторов.  
   **DE:** Attraktor-Klassifizierung.  
3. **RU:** Метаправила, меняющие топологию.  
   **DE:** Meta-Regeln, die Topologie ändern.

### Долгосрочно / Langfristig

1. **RU:** Информационные законы символической физики.  
   **DE:** Informationstheoretische Gesetze der symbolischen Physik.  
2. **RU:** Масштабирование до иерархий.  
   **DE:** Skalierung zu Hierarchien.

## 8. Оценка и верификация / Bewertung und Verifikation

**RU:** Сравнение предсказаний, анализ траекторий, визуализация режимов, устойчивость к шуму.  
**DE:** Vergleich von Vorhersagen, Trajektorienanalyse, Visualisierung von Modi, Robustheit gegenüber Rauschen.

## 9. Примечание (когнитивный контекст) / Hinweis (kognitiver Kontext)

**RU:** Человеческое мышление ограничено эвристиками; требуется визуализация и нормализация, чтобы выйти за пределы интуитивного восприятия сложной адаптивной динамики.  
**DE:** Das menschliche Denken ist durch Heuristiken begrenzt; Visualisierung und Normalisierung sind notwendig, um über intuitive Wahrnehmung hinauszugehen.

## Файлы / Артефакты / Dateien / Artefakte

- `model_v04.json` — базовая модель. / Grundmodell.  
- `symbolic_core.py` — движок. / Engine.  
- `main_gui.py` — интерфейс и автотест. / Schnittstelle und Autotest.  
- `symbolic_physics_research_article.pdf` — предыдущая версия статьи. / vorheriger Artikel.  
- Аналитические скрипты: `test_engine.py`, `phase_visualizer.py`, `param_scan.py`, `lyapunov.py`, `network_builder.py`. / Analyse-Skripte.
